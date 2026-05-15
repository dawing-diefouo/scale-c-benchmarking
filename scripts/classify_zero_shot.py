"""Zero-shot classification with MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7.

Reads label names from ``schema/taxonomy.json``, classifies text derived from any
JSONL row shape, and writes Scale_C records (see ``schema/schema.json``) to
``data/processed/classified.jsonl``.

Model: https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema" / "taxonomy.json"
PROCESSED = ROOT / "data" / "processed"
DEFAULT_OUT = PROCESSED / "classified.jsonl"
RAW_ROOT = ROOT / "data" / "raw"

DEFAULT_MODEL = "NDugar/deberta-v2-xlarge-mnli"
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


def pick_device() -> int | str:
    import torch

    if torch.cuda.is_available():
        return 0
    if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
        return "mps"
    return -1


def load_taxonomy(path: Path) -> tuple[list[str], dict[str, str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    labels = data["labels"]
    names = [str(x["name"]) for x in labels]
    ids = [str(x["id"]) for x in labels]
    if len(names) != len(set(names)):
        raise ValueError("taxonomy label names must be unique for this pipeline mapping")
    name_to_id = dict(zip(names, ids, strict=True))
    return names, name_to_id


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
    """Build classifier input from any JSONL object (dataset-agnostic)."""
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
    if "json_schema" in row and "question" not in row:
        return "code_configuration_analysis"
    if row.get("sentence_1") and row.get("sentence_2"):
        return "scenario_reasoning"
    if row.get("context") and row.get("question") and row.get("answers"):
        return "short_answer"
    if row.get("question") and (
        row.get("choices") or row.get("options") or row.get("option_a") or row.get("answer") is not None
    ):
        return "mcq_answering"
    if row.get("prompt") and row.get("code"):
        return "code_review"
    if row.get("question") or row.get("prompt"):
        return "open_explanation"
    return "open_explanation"


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


def build_record(
    *,
    record_id: str,
    row: dict[str, Any],
    input_path: Path,
    model: str,
    pred_id: str,
    pred_name: str,
    raw_scores: dict[str, float],
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "id": record_id,
        "benchmark": BENCHMARK,
        "version": SCHEMA_VERSION,
        "tier": DEFAULT_TIER,
        "task_type": infer_task_type(row),
        "metadata": {
            "difficulty": PLACEHOLDER,
            "source": infer_source(input_path),
            "language": infer_language(input_path, row),
            "risk_category": PLACEHOLDER,
            "cognitive_skill": PLACEHOLDER,
        },
        "classification": {
            "predicted_label": pred_id,
            "predicted_label_name": pred_name,
            "raw_scores": raw_scores,
            "classifier": {"model": model},
        },
        "payload": row,
    }
    evaluation = build_evaluation(row)
    if evaluation is not None:
        record["evaluation"] = evaluation
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "data" / "raw" / "huggingface" / "mmlu" / "computer_security" / "test.jsonl",
        help="JSONL file or directory tree (only *.jsonl files are processed).",
    )
    parser.add_argument(
        "--taxonomy",
        type=Path,
        default=SCHEMA,
        help="JSON file with { labels: [ { id, name, description? }, ... ] }.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUT,
        help="Append-only JSONL with Scale_C records (set --truncate to overwrite).",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="HF model id for zero-shot-classification.",
    )
    parser.add_argument(
        "--multi-label",
        action="store_true",
        help="If set, allow multiple labels above 0.5 * top score (HF multi_label semantics).",
    )
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="Overwrite output instead of appending.",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=None,
        help="Process at most this many non-empty JSONL rows (after --start), across all inputs.",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=0,
        help="Skip the first N non-empty JSONL rows (global across all input files).",
    )
    parser.add_argument(
        "--id-prefix",
        default="scale_c",
        help="Prefix for generated record ids (e.g. scale_c_000001).",
    )
    args = parser.parse_args()

    if not args.input.exists():
        raise SystemExit(
            f"Input not found: {args.input}\n"
            "Fetch data first or pass --input to an existing .jsonl file or directory."
        )
    if not args.taxonomy.is_file():
        raise SystemExit(f"Taxonomy not found: {args.taxonomy}")

    try:
        input_files = iter_jsonl_files(args.input)
    except (FileNotFoundError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc

    candidate_names, name_to_id = load_taxonomy(args.taxonomy)

    from transformers import pipeline

    device = pick_device()
    classifier = pipeline(
        "zero-shot-classification",
        model=args.model,
        device=device,
    )

    PROCESSED.mkdir(parents=True, exist_ok=True)
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
                result = classifier(
                    text,
                    candidate_names,
                    multi_label=args.multi_label,
                )

                labels_out = result["labels"]
                scores_out = result["scores"]
                raw_scores = {
                    name_to_id[name]: float(score)
                    for name, score in zip(labels_out, scores_out, strict=True)
                }
                top_name = labels_out[0]
                pred_id = name_to_id[top_name]

                record_id = f"{args.id_prefix}_{next_id:06d}"
                next_id += 1
                record = build_record(
                    record_id=record_id,
                    row=row,
                    input_path=input_path,
                    model=args.model,
                    pred_id=pred_id,
                    pred_name=top_name,
                    raw_scores=raw_scores,
                )
                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                seen += 1
                written += 1

            if args.max_rows is not None and written >= args.max_rows:
                break

    out_display = args.output.relative_to(ROOT) if args.output.is_relative_to(ROOT) else args.output
    print(
        f"Wrote {written} record(s) to {out_display} "
        f"from {len(input_files)} file(s) (model={args.model}, device={device})"
    )


if __name__ == "__main__":
    main()
