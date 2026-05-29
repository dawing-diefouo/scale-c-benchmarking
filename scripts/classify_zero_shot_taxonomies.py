"""Zero-shot classification with Scale_C topic and metadata taxonomies.

This is a taxonomy-aware variant of ``scripts/classify_zero_shot.py``. It keeps
the original leaf-topic classification from ``schema/taxonomy.json`` and can
also classify records against the newer taxonomy files in ``schema/taxonomies/``:

* tasks.json -> diagnostic scores when explicitly requested
* risks.json -> record["metadata"]["risk_category"]
* difficulty.json -> record["metadata"]["difficulty"]
* cognitive.json -> record["metadata"]["cognitive_skill"]
* tiers.json -> diagnostic scores when explicitly requested

Detailed scores for the extra taxonomy passes are written to
``record["classification"]["taxonomies"]``. By default, ``task_type`` and
``tier`` are inferred structurally because the row shape is more reliable than
zero-shot classification for those fields. Edit the ``DEFAULT_*`` block below or
override it with CLI flags.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema" / "taxonomy.json"
TAXONOMY_ROOT = ROOT / "schema" / "taxonomies"
PROCESSED = ROOT / "data" / "processed"
RAW_ROOT = ROOT / "data" / "raw"

# --- Run configuration (edit these, then: python scripts/classify_zero_shot_taxonomies.py) ---
DEFAULT_INPUT = ROOT / "data" / "raw" / "huggingface" / "mmlu" / "computer_security" / "test.jsonl"
DEFAULT_TOPIC_TAXONOMY = SCHEMA
DEFAULT_TAXONOMY_DIR = TAXONOMY_ROOT
DEFAULT_OUTPUT = PROCESSED / "classified_with_taxonomies.jsonl"
DEFAULT_MODEL = "NDugar/deberta-v2-xlarge-mnli"
DEFAULT_MULTI_LABEL = False
DEFAULT_TRUNCATE = False
DEFAULT_MAX_ROWS: int | None = None
DEFAULT_START = 0
DEFAULT_ID_PREFIX = "scale_c"
DEFAULT_EXTRA_TAXONOMIES = ("risks", "difficulty", "cognitive")

BENCHMARK = "scale_c"
SCHEMA_VERSION = 2
DEFAULT_TIER = 1
PLACEHOLDER = "-"

TEXT_KEYS = (
    "question",
    "text",
    "prompt",
    "instruction",
    "context",
    "sentence_1",
    "sentence_2",
    "premise",
    "hypothesis",
    "json_schema",
    "code",
    "passage",
    "article",
    "title",
    "claim",
    "statement",
)

CLOZE_MARKERS = ("____", "___", "[MASK]", "<mask>", "<blank>", "{blank}", "[blank]", "{{blank}}")
GENERATION_WORDS = ("generate", "create", "write", "draft", "produce", "build")
TRANSLATION_WORDS = ("translate", "translation", "localize", "localise", "german", "deutsch")


@dataclass(frozen=True)
class TaxonomyLabel:
    key: str
    name: str
    description: str
    candidate: str


@dataclass(frozen=True)
class Taxonomy:
    name: str
    labels: list[TaxonomyLabel]


def pick_device() -> int | str:
    import torch

    if torch.cuda.is_available():
        return 0
    if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
        return "mps"
    return -1


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def load_taxonomy(path: Path, *, name: str | None = None, use_descriptions: bool = True) -> Taxonomy:
    data = json.loads(path.read_text(encoding="utf-8"))
    raw_labels = data["labels"]
    labels: list[TaxonomyLabel] = []
    seen_candidates: set[str] = set()

    for raw in raw_labels:
        label_name = str(raw["name"])
        label_key = str(raw.get("id", label_name))
        description = str(raw.get("description", "")).strip()
        candidate = f"{label_name}: {description}" if use_descriptions and description else label_name
        if candidate in seen_candidates:
            raise ValueError(f"{path}: taxonomy candidate labels must be unique")
        seen_candidates.add(candidate)
        labels.append(
            TaxonomyLabel(
                key=label_key,
                name=label_name,
                description=description,
                candidate=candidate,
            )
        )

    return Taxonomy(name=name or path.stem, labels=labels)


def iter_jsonl_files(path: Path) -> list[Path]:
    if path.is_file():
        if path.suffix.lower() != ".jsonl":
            raise ValueError(f"Expected a .jsonl file, got: {path}")
        return [path]
    if path.is_dir():
        files = sorted(path.rglob("*.jsonl"))
        if not files:
            raise ValueError(f"No .jsonl files under: {path}")
        return files
    raise FileNotFoundError(path)


def iter_jsonl_rows(path: Path) -> Iterator[tuple[int, dict[str, Any]]]:
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            yield line_no, json.loads(line)


def _append_choice_lines(parts: list[str], row: dict[str, Any]) -> None:
    choices = row.get("choices")
    if isinstance(choices, list) and choices:
        parts.append("Choices:")
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for i, choice in enumerate(choices):
            pref = letters[i] if i < len(letters) else str(i)
            parts.append(f"  {pref}) {choice}")
        return
    if isinstance(choices, dict) and choices:
        parts.append("Choices:")
        for key, value in choices.items():
            parts.append(f"  {key}) {value}")
        return

    options = row.get("options")
    if isinstance(options, list) and options:
        parts.append("Options:")
        for opt in options:
            parts.append(f"  {opt}")
        return

    option_lines: list[str] = []
    for letter in "abcdefghijklmnopqrstuvwxyz":
        key = f"option_{letter}"
        if key in row and row[key] is not None:
            option_lines.append(f"  {letter.upper()}) {row[key]}")
    if option_lines:
        parts.append("Options:")
        parts.extend(option_lines)


def text_for_classification(row: dict[str, Any]) -> str:
    """Build classifier input from any JSONL object."""
    parts: list[str] = []
    for key in TEXT_KEYS:
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            parts.append(value.strip())
    _append_choice_lines(parts, row)

    labels = row.get("labels")
    if isinstance(labels, str) and labels.strip() and "sentence_1" in row:
        parts.append(f"Label: {labels.strip()}")

    if parts:
        return "\n\n".join(parts)
    return json.dumps(row, ensure_ascii=False)


def row_text(row: dict[str, Any]) -> str:
    values: list[str] = []
    for key in TEXT_KEYS + ("task_type", "subject", "category", "type"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            values.append(value.strip())
    return "\n".join(values).lower()


def has_choices(row: dict[str, Any]) -> bool:
    choices = row.get("choices")
    options = row.get("options")
    if isinstance(choices, (list, dict)) and bool(choices):
        return True
    if isinstance(options, (list, dict)) and bool(options):
        return True
    return any(row.get(f"option_{letter}") is not None for letter in "abcdefghijklmnopqrstuvwxyz")


def has_answer(row: dict[str, Any]) -> bool:
    return row.get("answer") is not None or row.get("answers") is not None or row.get("target") is not None


def looks_like_cloze(row: dict[str, Any]) -> bool:
    text = row_text(row)
    if any(marker.lower() in text for marker in CLOZE_MARKERS):
        return True
    return any(key in row for key in ("blank", "blanks", "cloze", "completion"))


def looks_like_generation_request(row: dict[str, Any]) -> bool:
    text = row_text(row)
    if any(key in row for key in ("output_schema", "generation_type", "instructions")):
        return True
    return any(word in text for word in GENERATION_WORDS)


def looks_like_translation_request(row: dict[str, Any]) -> bool:
    text = row_text(row)
    if any(key in row for key in ("source_language", "target_language", "translation")):
        return True
    return any(word in text for word in TRANSLATION_WORDS) or ("english" in text and "german" in text)


def looks_like_h5p_request(row: dict[str, Any]) -> bool:
    return "h5p" in row_text(row) or any(key.startswith("h5p") for key in row)


def infer_source(input_path: Path) -> str:
    try:
        rel = input_path.relative_to(RAW_ROOT)
        parts = rel.parts
        if len(parts) >= 2:
            return "/".join(parts[:-1])
        return rel.as_posix()
    except ValueError:
        return input_path.stem


_LANG_RE = re.compile(r"(^|[/\\])(en|de|fr|es|it|pt|nl|pl|ru|zh|ja|ko)([/\\]|$)", re.I)


def infer_language(input_path: Path, row: dict[str, Any]) -> str:
    for key in ("language", "lang", "locale"):
        val = row.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip().lower()[:8]
    path_str = input_path.as_posix()
    m = _LANG_RE.search(path_str)
    if m:
        return m.group(2).lower()
    if re.search(r"(^|[/\\])(german|deutsch|supergleber|germeval)([/\\_]|$)", path_str, re.I):
        return "de"
    return "en"


def infer_task_type(row: dict[str, Any]) -> str:
    existing = row.get("task_type")
    if isinstance(existing, str) and existing.strip():
        return existing.strip()
    if looks_like_translation_request(row):
        return "translation_en_de"
    if looks_like_generation_request(row):
        text = row_text(row)
        if looks_like_h5p_request(row):
            if "german" in text or "deutsch" in text:
                return "german_h5p_generation"
            if has_choices(row) or "multiple-choice" in text or "multiple choice" in text:
                return "h5p_mcq_generation"
            return "h5p_structured_generation"
        if looks_like_cloze(row):
            return "cloze_generation"
        if has_choices(row) or "multiple-choice" in text or "multiple choice" in text:
            return "mcq_generation"
        if "german" in text or "deutsch" in text:
            return "german_content_generation"
    if "json_schema" in row and "question" not in row:
        return "code_configuration_analysis"
    if row.get("sentence_1") and row.get("sentence_2"):
        return "scenario_reasoning"
    if row.get("context") and row.get("question") and row.get("answers"):
        return "short_answer"
    if row.get("question") and has_choices(row):
        return "mcq_answering"
    if looks_like_cloze(row) and has_answer(row):
        return "short_answer"
    if row.get("question") and has_answer(row):
        return "short_answer"
    if row.get("prompt") and row.get("code"):
        return "code_configuration_analysis"
    if row.get("code") or row.get("json_schema"):
        return "code_configuration_analysis"
    if row.get("question") or row.get("prompt"):
        return "open_explanation"
    return "open_explanation"


def infer_tier(task_type: str, input_path: Path, row: dict[str, Any]) -> int:
    language = infer_language(input_path, row)
    if task_type in {"translation_en_de", "german_content_generation", "german_h5p_generation"}:
        return 3
    if language == "de":
        return 3
    if task_type in {"mcq_generation", "cloze_generation", "h5p_structured_generation", "h5p_mcq_generation"}:
        return 2
    return DEFAULT_TIER


def tier_label_name(tier: int) -> str:
    return {
        1: "tier1_cyber_competence",
        2: "tier2_structured_generation",
        3: "tier3_multilingual_localization",
    }.get(tier, f"tier{tier}")


def _index_to_letter(index: int) -> str | None:
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if 0 <= index < len(letters):
        return letters[index]
    return None


def build_evaluation(row: dict[str, Any]) -> dict[str, Any] | None:
    if "answer" in row:
        ans = row["answer"]
        if isinstance(ans, int):
            letter = _index_to_letter(ans)
            if letter is not None:
                return {"scoring_type": "exact_match", "correct_answer": letter, "max_score": 1}
        if isinstance(ans, str) and ans.strip():
            return {"scoring_type": "exact_match", "correct_answer": ans.strip(), "max_score": 1}
    if "answers" in row and row["answers"] is not None:
        if isinstance(row["answers"], dict) and row["answers"].get("text"):
            texts = row["answers"]["text"]
            if isinstance(texts, list) and texts:
                return {"scoring_type": "exact_match", "correct_answer": texts[0], "max_score": 1}
        return {"scoring_type": "exact_match", "correct_answer": row["answers"], "max_score": 1}
    return None


def classify_taxonomy(
    classifier: Any,
    text: str,
    taxonomy: Taxonomy,
    *,
    multi_label: bool,
) -> dict[str, Any]:
    by_candidate = {label.candidate: label for label in taxonomy.labels}
    result = classifier(
        text,
        list(by_candidate),
        multi_label=multi_label,
    )

    labels_out = result["labels"]
    scores_out = result["scores"]
    raw_scores: dict[str, float] = {}
    for candidate, score in zip(labels_out, scores_out, strict=True):
        label = by_candidate[candidate]
        raw_scores[label.key] = float(score)

    top_label = by_candidate[labels_out[0]]
    top_score = float(scores_out[0])
    runner_up_score = float(scores_out[1]) if len(scores_out) > 1 else 0.0
    margin = top_score - runner_up_score
    if top_score >= 0.6 and margin >= 0.2:
        confidence = "high"
    elif top_score >= 0.35 and margin >= 0.1:
        confidence = "medium"
    else:
        confidence = "low"
    return {
        "predicted_label": top_label.key,
        "predicted_label_name": top_label.name,
        "raw_scores": raw_scores,
        "top_score": top_score,
        "margin": margin,
        "confidence": confidence,
        "method": "zero_shot",
    }


def build_record(
    *,
    record_id: str,
    row: dict[str, Any],
    input_path: Path,
    model: str,
    topic_result: dict[str, Any],
    taxonomy_results: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    task_type = infer_task_type(row)
    difficulty = taxonomy_results.get("difficulty", {}).get("predicted_label_name", PLACEHOLDER)
    risk_category = taxonomy_results.get("risks", {}).get("predicted_label_name", PLACEHOLDER)
    cognitive_skill = taxonomy_results.get("cognitive", {}).get("predicted_label_name", PLACEHOLDER)
    tier = infer_tier(task_type, input_path, row)

    record: dict[str, Any] = {
        "id": record_id,
        "benchmark": BENCHMARK,
        "version": SCHEMA_VERSION,
        "tier": tier,
        "task_type": task_type,
        "metadata": {
            "difficulty": difficulty,
            "source": infer_source(input_path),
            "language": infer_language(input_path, row),
            "risk_category": risk_category,
            "cognitive_skill": cognitive_skill,
        },
        "classification": {
            "predicted_label": topic_result["predicted_label"],
            "predicted_label_name": topic_result["predicted_label_name"],
            "raw_scores": topic_result["raw_scores"],
            "top_score": topic_result["top_score"],
            "margin": topic_result["margin"],
            "confidence": topic_result["confidence"],
            "classifier": {"model": model},
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
    if taxonomy_results:
        record["classification"]["taxonomies"] = taxonomy_results

    evaluation = build_evaluation(row)
    if evaluation is not None:
        record["evaluation"] = evaluation
    return record


def load_extra_taxonomies(taxonomy_dir: Path, names: list[str]) -> dict[str, Taxonomy]:
    taxonomies: dict[str, Taxonomy] = {}
    for name in names:
        path = taxonomy_dir / f"{name}.json"
        if not path.is_file():
            raise FileNotFoundError(f"Taxonomy not found: {path}")
        taxonomies[name] = load_taxonomy(path, name=name)
    return taxonomies


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"JSONL file or directory tree (default: {DEFAULT_INPUT}).",
    )
    parser.add_argument(
        "--topic-taxonomy",
        type=Path,
        default=DEFAULT_TOPIC_TAXONOMY,
        help=f"Leaf topic taxonomy JSON (default: {DEFAULT_TOPIC_TAXONOMY}).",
    )
    parser.add_argument(
        "--taxonomy-dir",
        type=Path,
        default=DEFAULT_TAXONOMY_DIR,
        help=f"Directory with extra taxonomy JSON files (default: {DEFAULT_TAXONOMY_DIR}).",
    )
    parser.add_argument(
        "--extra-taxonomies",
        nargs="*",
        choices=("tasks", "risks", "difficulty", "cognitive", "tiers"),
        default=list(DEFAULT_EXTRA_TAXONOMIES),
        help="Extra taxonomies to classify. Pass no values after the flag to disable them.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Append-only Scale_C JSONL (default: {DEFAULT_OUTPUT}; use --truncate to overwrite).",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"HF zero-shot-classification model id (default: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--multi-label",
        action=argparse.BooleanOptionalAction,
        default=DEFAULT_MULTI_LABEL,
        help="Use HF multi_label semantics for all taxonomy passes.",
    )
    parser.add_argument(
        "--truncate",
        action=argparse.BooleanOptionalAction,
        default=DEFAULT_TRUNCATE,
        help="Overwrite output instead of appending.",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=DEFAULT_MAX_ROWS,
        help="Process at most this many non-empty JSONL rows (after --start), across all inputs.",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=DEFAULT_START,
        help="Skip the first N non-empty JSONL rows (global across all input files).",
    )
    parser.add_argument(
        "--id-prefix",
        default=DEFAULT_ID_PREFIX,
        help=f"Prefix for generated record ids (default: {DEFAULT_ID_PREFIX}).",
    )
    args = parser.parse_args()

    if not args.input.exists():
        raise SystemExit(
            f"Input not found: {args.input}\n"
            "Fetch data first or pass --input to an existing .jsonl file or directory."
        )
    if not args.topic_taxonomy.is_file():
        raise SystemExit(f"Topic taxonomy not found: {args.topic_taxonomy}")
    if args.extra_taxonomies and not args.taxonomy_dir.is_dir():
        raise SystemExit(f"Taxonomy directory not found: {args.taxonomy_dir}")

    try:
        input_files = iter_jsonl_files(args.input)
        topic_taxonomy = load_taxonomy(args.topic_taxonomy, name="topics")
        extra_taxonomies = load_extra_taxonomies(args.taxonomy_dir, args.extra_taxonomies)
    except (FileNotFoundError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc

    from transformers import pipeline

    device = pick_device()
    classifier = pipeline(
        "zero-shot-classification",
        model=args.model,
        device=device,
    )

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
                topic_result = classify_taxonomy(
                    classifier,
                    text,
                    topic_taxonomy,
                    multi_label=args.multi_label,
                )
                taxonomy_results = {
                    name: classify_taxonomy(classifier, text, taxonomy, multi_label=args.multi_label)
                    for name, taxonomy in extra_taxonomies.items()
                }

                record_id = f"{args.id_prefix}_{next_id:06d}"
                next_id += 1
                record = build_record(
                    record_id=record_id,
                    row=row,
                    input_path=input_path,
                    model=args.model,
                    topic_result=topic_result,
                    taxonomy_results=taxonomy_results,
                )
                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                seen += 1
                written += 1

            if args.max_rows is not None and written >= args.max_rows:
                break

    print(
        f"Wrote {written} record(s) to {display_path(args.output)} "
        f"from {len(input_files)} file(s) "
        f"(model={args.model}, device={device}, extra_taxonomies={','.join(extra_taxonomies) or 'none'})"
    )


if __name__ == "__main__":
    main()
