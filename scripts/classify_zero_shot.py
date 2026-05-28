"""Zero-shot classification with MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7.

Reads label names from ``schema/taxonomy.json``, classifies text derived from any
JSONL row shape, and writes Scale_C records (see ``schema/schema.json``) to
``data/processed/``. Edit the ``DEFAULT_*`` run configuration block at the top of
this file, then run with no CLI arguments; flags still override those defaults.

Model: https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7
"""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema" / "taxonomy.json"
PROCESSED = ROOT / "data" / "processed"
RAW_ROOT = ROOT / "data" / "raw"

# --- Run configuration (edit these, then: python scripts/classify_zero_shot.py) ---
DEFAULT_INPUT = ROOT / "data" / "raw" / "huggingface" / "mmlu" / "computer_security" / "test.jsonl"
DEFAULT_TAXONOMY = SCHEMA
DEFAULT_OUTPUT = PROCESSED / "classified_mmlu_cs_test.jsonl"
DEFAULT_MODEL = "microsoft/LLM2CLIP-Llama-3-8B-Instruct-CC-Finetuned"
DEFAULT_MULTI_LABEL = False
DEFAULT_TRUNCATE = False
DEFAULT_MAX_ROWS: int | None = None
DEFAULT_START = 0
DEFAULT_ID_PREFIX = "scale_c"

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


def pick_device(requested: str) -> int | str:
    """Map CLI device choice to Transformers pipeline ``device`` (-1 = CPU)."""
    import torch

    if requested == "cpu":
        return -1
    if requested == "cuda":
        if not torch.cuda.is_available():
            raise SystemExit(
                "CUDA was requested (--device cuda) but is not available. "
                "Update the NVIDIA driver, install a matching PyTorch build, or use --device cpu."
            )
        return 0
    if requested == "mps":
        mps = getattr(torch.backends, "mps", None)
        if mps is None or not mps.is_available():
            raise SystemExit("--device mps was requested but Apple MPS is not available.")
        return "mps"
    # auto: prefer CUDA, then MPS, else CPU
    if torch.cuda.is_available():
        return 0
    mps = getattr(torch.backends, "mps", None)
    if mps is not None and mps.is_available():
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


def resolve_output_path(*, input_root: Path, input_path: Path, output_arg: Path) -> Path:
    """
    If classifying a directory tree, mirror the input structure under an output directory.

    - input_root is the --input argument (a directory)
    - input_path is a concrete .jsonl file within that tree
    - output_arg is the --output argument (interpreted as a directory or file)
    """
    # If output looks like a file path (has a suffix), derive a directory from it.
    # This keeps CLI backwards compatibility when users forget to switch --output to a dir.
    out_base = output_arg
    if out_base.suffix:
        out_base = out_base.parent / out_base.stem
    rel = input_path.relative_to(input_root)
    return out_base / rel


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
        default=DEFAULT_INPUT,
        help=f"JSONL file or directory tree (default: {DEFAULT_INPUT}).",
    )
    parser.add_argument(
        "--taxonomy",
        type=Path,
        default=DEFAULT_TAXONOMY,
        help=f"Label taxonomy JSON (default: {DEFAULT_TAXONOMY}).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=(
            f"Output path. If --input is a file, this is a JSONL file (default: {DEFAULT_OUTPUT}). "
            "If --input is a directory, this is treated as an output directory and the input tree is "
            "mirrored under it (one output .jsonl per input .jsonl). If a file path is provided in "
            "directory mode, its stem is used as the output directory name."
        ),
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
        help="Allow multiple labels above 0.5 * top score (HF multi_label semantics).",
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
    parser.add_argument(
        "--device",
        choices=("auto", "cpu", "cuda", "mps"),
        default="auto",
        help=(
            "Inference device. Use cpu when the NVIDIA driver is older than the PyTorch CUDA build "
            "(avoids CUDA init warnings). Default: auto (cuda if available, else mps, else cpu)."
        ),
    )
    args = parser.parse_args()

    if args.device == "cpu":
        os.environ["CUDA_VISIBLE_DEVICES"] = ""

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

    device = pick_device(args.device)
    classifier = pipeline(
        "zero-shot-classification",
        model=args.model,
        device=device,
    )

    PROCESSED.mkdir(parents=True, exist_ok=True)
    seen = 0
    written = 0
    next_id = 1

    if args.input.is_dir():
        out_base = args.output
        if out_base.suffix:
            out_base = out_base.parent / out_base.stem
        out_base.mkdir(parents=True, exist_ok=True)

        output_paths: list[Path] = []
        for input_path in input_files:
            out_path = resolve_output_path(input_root=args.input, input_path=input_path, output_arg=args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            output_paths.append(out_path)
            mode = "w" if args.truncate else "a"
            with out_path.open(mode, encoding="utf-8") as out_f:
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

        out_display = out_base.relative_to(ROOT) if out_base.is_relative_to(ROOT) else out_base
        print(
            f"Wrote {written} record(s) under {out_display} "
            f"from {len(input_files)} file(s) (model={args.model}, device={device})"
        )
    else:
        mode = "w" if args.truncate else "a"
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
