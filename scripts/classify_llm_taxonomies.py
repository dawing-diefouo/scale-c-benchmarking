"""LLM-based taxonomy classification for Scale_C JSONL rows.

This script keeps the reliable structural decisions from
``classify_zero_shot_taxonomies.py`` for ``task_type`` and ``tier``, then uses an
LLM with taxonomy rubrics for semantic labels: topic, risk, difficulty, and
cognitive skill.

Configuration is intentionally similar to the zero-shot script. The default
target is an OpenAI-compatible local server, e.g. vLLM serving Qwen3-32B at
``http://localhost:8000/v1``. Edit the ``DEFAULT_*`` block if desired, or
override values with CLI flags.
"""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from classify_zero_shot_taxonomies import (
    BENCHMARK,
    PLACEHOLDER,
    PROCESSED,
    ROOT,
    SCHEMA,
    SCHEMA_VERSION,
    TAXONOMY_ROOT,
    Taxonomy,
    build_evaluation,
    display_path,
    infer_language,
    infer_source,
    infer_task_type,
    infer_tier,
    iter_jsonl_files,
    iter_jsonl_rows,
    load_taxonomy,
    text_for_classification,
    tier_label_name,
)

# --- Run configuration (edit these, then: python scripts/classify_llm_taxonomies.py) ---
DEFAULT_INPUT = ROOT / "data" / "raw" / "huggingface" / "mmlu" / "computer_security" / "task_types.jsonl"
DEFAULT_TOPIC_TAXONOMY = SCHEMA
DEFAULT_TAXONOMY_DIR = TAXONOMY_ROOT
DEFAULT_OUTPUT = PROCESSED / "classified_llm_taxonomies.jsonl"
DEFAULT_MODEL = os.environ.get("LLM_MODEL", "Qwen3-32B")
DEFAULT_API_BASE = os.environ.get("LLM_API_BASE", "http://localhost:8000/v1")
DEFAULT_API_KEY_ENV = "LLM_API_KEY"
DEFAULT_RESPONSE_FORMAT = "json_schema"
DEFAULT_TRUNCATE = False
DEFAULT_MAX_ROWS: int | None = None
DEFAULT_START = 0
DEFAULT_ID_PREFIX = "scale_c"
DEFAULT_SEMANTIC_TAXONOMIES = ("topics", "risks", "difficulty", "cognitive")

CONFIDENCE_SCORE = {
    "high": 1.0,
    "medium": 0.66,
    "low": 0.33,
}


def taxonomy_options(taxonomy: Taxonomy) -> str:
    lines: list[str] = []
    for label in taxonomy.labels:
        suffix = f" - {label.description}" if label.description else ""
        lines.append(f"- {label.key}: {label.name}{suffix}")
    return "\n".join(lines)


def label_name_by_key(taxonomy: Taxonomy) -> dict[str, str]:
    return {label.key: label.name for label in taxonomy.labels}


def semantic_schema(taxonomies: dict[str, Taxonomy]) -> dict[str, Any]:
    properties: dict[str, Any] = {}
    required: list[str] = []
    for name, taxonomy in taxonomies.items():
        required.append(name)
        properties[name] = {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "predicted_label": {
                    "type": "string",
                    "enum": [label.key for label in taxonomy.labels],
                },
                "confidence": {
                    "type": "string",
                    "enum": ["high", "medium", "low"],
                },
                "reason": {
                    "type": "string",
                    "description": "One concise sentence explaining the choice.",
                },
            },
            "required": ["predicted_label", "confidence", "reason"],
        }
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": required,
    }


def build_messages(
    *,
    row: dict[str, Any],
    text: str,
    task_type: str,
    tier: int,
    taxonomies: dict[str, Taxonomy],
) -> list[dict[str, str]]:
    rubric_sections = "\n\n".join(
        f"{name.upper()} TAXONOMY\n{taxonomy_options(taxonomy)}"
        for name, taxonomy in taxonomies.items()
    )
    developer = (
        "You classify benchmark rows into Scale_C taxonomies. "
        "Choose exactly one label per requested taxonomy. "
        "Use the taxonomy definitions, the row payload, and the structural "
        "task_type/tier hints. Prefer the most specific label. "
        "Set confidence to high only when the evidence is clear, medium when "
        "two labels are plausible but one is stronger, and low when the choice "
        "is genuinely ambiguous. Return only JSON matching the schema."
    )
    json_contract = {
        name: {
            "predicted_label": [label.key for label in taxonomy.labels],
            "confidence": ["high", "medium", "low"],
            "reason": "one concise sentence",
        }
        for name, taxonomy in taxonomies.items()
    }
    user = (
        f"STRUCTURAL HINTS\n"
        f"task_type: {task_type}\n"
        f"tier: {tier}\n\n"
        f"{rubric_sections}\n\n"
        f"REQUIRED JSON SHAPE\n{json.dumps(json_contract, ensure_ascii=False)}\n\n"
        f"CLASSIFICATION TEXT\n{text}\n\n"
        f"RAW PAYLOAD\n{json.dumps(row, ensure_ascii=False)}"
    )
    return [
        {"role": "system", "content": developer},
        {"role": "user", "content": user},
    ]


def call_openai_chat(
    *,
    api_key: str | None,
    api_base: str,
    model: str,
    messages: list[dict[str, str]],
    schema: dict[str, Any],
    response_format: str,
    timeout: float,
    retries: int,
) -> dict[str, Any]:
    url = api_base.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0,
    }
    if response_format == "json_schema":
        payload["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": "scale_c_taxonomy_classification",
                "strict": True,
                "schema": schema,
            },
        }
    elif response_format == "json_object":
        payload["response_format"] = {"type": "json_object"}
    elif response_format != "none":
        raise ValueError(f"Unsupported response format: {response_format}")

    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers=headers,
    )

    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            return parse_json_content(content)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError, KeyError) as exc:
            if attempt >= retries:
                raise RuntimeError(f"LLM request failed after {retries + 1} attempt(s): {exc}") from exc
            time.sleep(2**attempt)

    raise RuntimeError("LLM request failed unexpectedly")


def parse_json_content(content: str) -> dict[str, Any]:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(content[start : end + 1])


def llm_result_to_classification(
    *,
    name: str,
    taxonomy: Taxonomy,
    result: dict[str, Any],
) -> dict[str, Any]:
    pred_id = str(result["predicted_label"])
    names = label_name_by_key(taxonomy)
    if pred_id not in names:
        valid = ", ".join(names)
        raise ValueError(f"{name}: invalid predicted_label {pred_id!r}; expected one of: {valid}")
    confidence = str(result["confidence"])
    if confidence not in CONFIDENCE_SCORE:
        raise ValueError(f"{name}: invalid confidence {confidence!r}; expected high, medium, or low")
    score = CONFIDENCE_SCORE.get(confidence, CONFIDENCE_SCORE["low"])
    return {
        "predicted_label": pred_id,
        "predicted_label_name": names[pred_id],
        "raw_scores": {pred_id: score},
        "confidence": confidence,
        "confidence_score": score,
        "method": "llm_rubric",
        "reason": str(result["reason"]).strip(),
        "score_note": "LLM confidence mapped high=1.0, medium=0.66, low=0.33; not a calibrated probability.",
        "taxonomy": name,
    }


def build_record(
    *,
    record_id: str,
    row: dict[str, Any],
    input_path: Path,
    model: str,
    semantic_results: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    task_type = infer_task_type(row)
    tier = infer_tier(task_type, input_path, row)
    topic_result = semantic_results.get("topics")

    if topic_result is None:
        topic_result = {
            "predicted_label": PLACEHOLDER,
            "predicted_label_name": PLACEHOLDER,
            "raw_scores": {},
            "confidence": "low",
            "confidence_score": CONFIDENCE_SCORE["low"],
            "method": "not_classified",
            "reason": "Topic classification was not requested.",
        }

    record: dict[str, Any] = {
        "id": record_id,
        "benchmark": BENCHMARK,
        "version": SCHEMA_VERSION,
        "tier": tier,
        "task_type": task_type,
        "metadata": {
            "difficulty": semantic_results.get("difficulty", {}).get("predicted_label_name", PLACEHOLDER),
            "source": infer_source(input_path),
            "language": infer_language(input_path, row),
            "risk_category": semantic_results.get("risks", {}).get("predicted_label_name", PLACEHOLDER),
            "cognitive_skill": semantic_results.get("cognitive", {}).get("predicted_label_name", PLACEHOLDER),
        },
        "classification": {
            "predicted_label": topic_result["predicted_label"],
            "predicted_label_name": topic_result["predicted_label_name"],
            "raw_scores": topic_result["raw_scores"],
            "confidence": topic_result["confidence"],
            "confidence_score": topic_result["confidence_score"],
            "method": topic_result["method"],
            "reason": topic_result["reason"],
            "classifier": {"model": model, "backend": "openai_compatible_chat_completions"},
            "taxonomy_decisions": {
                "tasks": {
                    "predicted_label": task_type,
                    "predicted_label_name": task_type,
                    "confidence": "high",
                    "method": "structural",
                },
                "tiers": {
                    "predicted_label": tier_label_name(tier),
                    "predicted_label_name": tier_label_name(tier),
                    "confidence": "high",
                    "method": "structural",
                },
            },
        },
        "payload": row,
    }

    extra_results = {key: value for key, value in semantic_results.items() if key != "topics"}
    if extra_results:
        record["classification"]["taxonomies"] = extra_results

    evaluation = build_evaluation(row)
    if evaluation is not None:
        record["evaluation"] = evaluation
    return record


def load_semantic_taxonomies(
    *,
    topic_taxonomy: Path,
    taxonomy_dir: Path,
    names: list[str],
) -> dict[str, Taxonomy]:
    taxonomies: dict[str, Taxonomy] = {}
    if "topics" in names:
        taxonomies["topics"] = load_taxonomy(topic_taxonomy, name="topics")
    for name in names:
        if name == "topics":
            continue
        path = taxonomy_dir / f"{name}.json"
        if not path.is_file():
            raise FileNotFoundError(f"Taxonomy not found: {path}")
        taxonomies[name] = load_taxonomy(path, name=name)
    return taxonomies


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--topic-taxonomy", type=Path, default=DEFAULT_TOPIC_TAXONOMY)
    parser.add_argument("--taxonomy-dir", type=Path, default=DEFAULT_TAXONOMY_DIR)
    parser.add_argument(
        "--semantic-taxonomies",
        nargs="+",
        choices=("topics", "risks", "difficulty", "cognitive"),
        default=list(DEFAULT_SEMANTIC_TAXONOMIES),
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--api-base", default=DEFAULT_API_BASE)
    parser.add_argument(
        "--api-key-env",
        default=DEFAULT_API_KEY_ENV,
        help="Environment variable containing an API key. Leave unset for local servers that do not require auth.",
    )
    parser.add_argument(
        "--require-api-key",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Require --api-key-env to be set. Usually false for local Qwen/vLLM servers.",
    )
    parser.add_argument(
        "--response-format",
        choices=("json_schema", "json_object", "none"),
        default=DEFAULT_RESPONSE_FORMAT,
        help="Use json_schema when the server supports structured outputs; use json_object or none as fallback.",
    )
    parser.add_argument("--truncate", action=argparse.BooleanOptionalAction, default=DEFAULT_TRUNCATE)
    parser.add_argument("--max-rows", type=int, default=DEFAULT_MAX_ROWS)
    parser.add_argument("--start", type=int, default=DEFAULT_START)
    parser.add_argument("--id-prefix", default=DEFAULT_ID_PREFIX)
    parser.add_argument("--request-timeout", type=float, default=60.0)
    parser.add_argument("--retries", type=int, default=2)
    args = parser.parse_args()

    api_key = os.environ.get(args.api_key_env)
    if args.require_api_key and not api_key:
        raise SystemExit(f"Missing API key: set {args.api_key_env}")
    if not args.input.exists():
        raise SystemExit(f"Input not found: {args.input}")
    if not args.topic_taxonomy.is_file():
        raise SystemExit(f"Topic taxonomy not found: {args.topic_taxonomy}")

    try:
        input_files = iter_jsonl_files(args.input)
        taxonomies = load_semantic_taxonomies(
            topic_taxonomy=args.topic_taxonomy,
            taxonomy_dir=args.taxonomy_dir,
            names=args.semantic_taxonomies,
        )
    except (FileNotFoundError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc

    schema = semantic_schema(taxonomies)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    mode = "w" if args.truncate else "a"
    seen = 0
    written = 0
    next_id = 1

    with args.output.open(mode, encoding="utf-8") as out_f:
        for input_path in input_files:
            for line_no, row in iter_jsonl_rows(input_path):
                if args.start > 0 and seen < args.start:
                    seen += 1
                    continue
                if args.max_rows is not None and written >= args.max_rows:
                    break

                text = text_for_classification(row)
                task_type = infer_task_type(row)
                tier = infer_tier(task_type, input_path, row)
                messages = build_messages(
                    row=row,
                    text=text,
                    task_type=task_type,
                    tier=tier,
                    taxonomies=taxonomies,
                )
                llm_payload = call_openai_chat(
                    api_key=api_key,
                    api_base=args.api_base,
                    model=args.model,
                    messages=messages,
                    schema=schema,
                    response_format=args.response_format,
                    timeout=args.request_timeout,
                    retries=args.retries,
                )
                semantic_results = {
                    name: llm_result_to_classification(name=name, taxonomy=taxonomy, result=llm_payload[name])
                    for name, taxonomy in taxonomies.items()
                }

                record_id = f"{args.id_prefix}_{next_id:06d}"
                next_id += 1
                record = build_record(
                    record_id=record_id,
                    row=row,
                    input_path=input_path,
                    model=args.model,
                    semantic_results=semantic_results,
                )
                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                seen += 1
                written += 1

            if args.max_rows is not None and written >= args.max_rows:
                break

    print(
        f"Wrote {written} record(s) to {display_path(args.output)} "
        f"from {len(input_files)} file(s) "
        f"(model={args.model}, semantic_taxonomies={','.join(taxonomies)})"
    )


if __name__ == "__main__":
    main()
