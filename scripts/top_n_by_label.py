"""Select top-N classified rows (optional per predicted_label, optional threshold).

Reads Scale_C JSONL records (see ``schema/schema.json``), ranks each row by
``raw_scores[classification.predicted_label]``, and keeps up to N rows.

With ``--per-predicted-label`` (default), keeps up to N rows **per**
``classification.predicted_label``. Without it, keeps the N highest-scoring rows
**overall** in each file.

Without ``--threshold``, no score cutoff. With ``--threshold``, only rows with
score >= that value are eligible.

Pass a classified JSONL file or a directory tree. For each ``*.jsonl`` under the
directory (recursively), writes prefixed output in the same folder
(``top_n{N}_`` or ``top_n{N}_global_``). Existing ``top_n*`` outputs are skipped.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

# --- Run configuration (edit these, then: python scripts/top_n_by_label.py) ---
DEFAULT_INPUT = PROCESSED / "SEC-bench"
DEFAULT_TOP_N = 10
DEFAULT_PER_PREDICTED_LABEL = True
DEFAULT_SAVE = True

_TOP_N_OUTPUT_RE = re.compile(r"^top_n\d+_(?:global_)?.*\.jsonl$", re.IGNORECASE)


def output_prefix(top_n: int, *, per_predicted_label: bool) -> str:
    if per_predicted_label:
        return f"top_n{top_n}_"
    return f"top_n{top_n}_global_"


def is_top_n_output(path: Path) -> bool:
    return bool(_TOP_N_OUTPUT_RE.match(path.name))


def iter_input_jsonl_files(path: Path) -> list[Path]:
    if path.is_file():
        if path.suffix.lower() != ".jsonl":
            raise ValueError(f"Expected a .jsonl file, got: {path}")
        if is_top_n_output(path):
            raise ValueError(
                f"Input looks like a top_n output file; pass the classified source: {path}"
            )
        return [path]
    if path.is_dir():
        files = sorted(
            p
            for p in path.rglob("*.jsonl")
            if p.is_file() and not is_top_n_output(p)
        )
        if not files:
            raise ValueError(f"No .jsonl files under: {path}")
        return files
    raise FileNotFoundError(path)


def resolve_output_path(
    *,
    input_root: Path,
    input_path: Path,
    top_n: int,
    per_predicted_label: bool,
    output_arg: Path | None,
) -> Path:
    prefixed_name = f"{output_prefix(top_n, per_predicted_label=per_predicted_label)}{input_path.name}"
    if output_arg is None:
        return input_path.parent / prefixed_name
    if input_root.is_file():
        return output_arg
    out_base = output_arg
    if out_base.suffix.lower() == ".jsonl":
        out_base = out_base.parent / out_base.stem
    rel = input_path.relative_to(input_root)
    return out_base / rel.parent / prefixed_name


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def predicted_score(record: dict[str, Any]) -> tuple[str, float] | None:
    classification = record.get("classification")
    if not isinstance(classification, dict):
        return None

    pred_id = classification.get("predicted_label")
    raw_scores = classification.get("raw_scores")
    if not isinstance(pred_id, str) or not isinstance(raw_scores, dict):
        return None

    score = raw_scores.get(pred_id)
    if score is None:
        return None
    try:
        return pred_id, float(score)
    except (TypeError, ValueError):
        return None


def iter_records(path: Path) -> Iterator[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_no}: expected a JSON object")
            yield row


def select_top_n(
    records: list[dict[str, Any]],
    *,
    top_n: int,
    min_score: float | None = None,
    per_predicted_label: bool = True,
) -> list[dict[str, Any]]:
    scored: list[tuple[float, str, dict[str, Any]]] = []

    for record in records:
        parsed = predicted_score(record)
        if parsed is None:
            continue
        pred_id, score = parsed
        if min_score is not None and score < min_score:
            continue
        scored.append((score, pred_id, record))

    if not per_predicted_label:
        scored.sort(key=lambda item: item[0], reverse=True)
        return [record for _, _, record in scored[:top_n]]

    by_label: dict[str, list[tuple[float, dict[str, Any]]]] = defaultdict(list)
    for score, pred_id, record in scored:
        by_label[pred_id].append((score, record))

    selected: list[tuple[float, str, dict[str, Any]]] = []
    for pred_id, label_scored in by_label.items():
        label_scored.sort(key=lambda item: item[0], reverse=True)
        for score, record in label_scored[:top_n]:
            selected.append((score, pred_id, record))

    selected.sort(key=lambda item: (item[1], -item[0]))
    return [record for _, _, record in selected]


def process_file(
    input_path: Path,
    output_path: Path,
    *,
    top_n: int,
    min_score: float | None,
    per_predicted_label: bool,
    save: bool,
) -> dict[str, Any]:
    records = list(iter_records(input_path))
    kept = select_top_n(
        records,
        top_n=top_n,
        min_score=min_score,
        per_predicted_label=per_predicted_label,
    )

    if save:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as out_f:
            for record in kept:
                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")

    per_label: dict[str, int] = defaultdict(int)
    for record in kept:
        parsed = predicted_score(record)
        if parsed:
            per_label[parsed[0]] += 1

    labels_in = len({predicted_score(r)[0] for r in records if predicted_score(r)})
    labels_out = len(per_label)
    return {
        "input_path": input_path,
        "output_path": output_path,
        "records_in": len(records),
        "records_out": len(kept),
        "labels_in": labels_in,
        "labels_out": labels_out,
        "per_label": dict(per_label),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Classified JSONL file or directory tree (default: {DEFAULT_INPUT}).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Output path for a single input file, or output root directory when "
            "--input is a directory (default: top_n{N}_<filename> beside each input)."
        ),
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=DEFAULT_TOP_N,
        help=f"Maximum rows to keep (default: {DEFAULT_TOP_N}).",
    )
    per_label_group = parser.add_mutually_exclusive_group()
    per_label_group.add_argument(
        "--per-predicted-label",
        dest="per_predicted_label",
        action="store_true",
        default=DEFAULT_PER_PREDICTED_LABEL,
        help="Keep up to N rows per classification.predicted_label (default).",
    )
    per_label_group.add_argument(
        "--no-per-predicted-label",
        dest="per_predicted_label",
        action="store_false",
        help="Keep the N highest-scoring rows overall (ignores label buckets).",
    )
    parser.add_argument(
        "--min-score",
        "--threshold",
        dest="min_score",
        type=float,
        default=None,
        help=(
            "Keep only rows with raw_scores[predicted_label] >= this value. "
            "Omit to take the top N highest-scoring rows per label with no cutoff."
        ),
    )
    save_group = parser.add_mutually_exclusive_group()
    save_group.add_argument(
        "--save",
        dest="save",
        action="store_true",
        default=DEFAULT_SAVE,
        help="Write selected rows to --output (default).",
    )
    save_group.add_argument(
        "--no-save",
        dest="save",
        action="store_false",
        help="Only print selection stats; do not write JSONL.",
    )
    args = parser.parse_args()

    if args.top_n < 1:
        raise SystemExit("--top-n must be at least 1")
    if args.min_score is not None and not (0.0 <= args.min_score <= 1.0):
        raise SystemExit("--min-score / --threshold must be between 0 and 1")
    if not args.input.exists():
        raise SystemExit(f"Input not found: {args.input}")
    if args.input.is_dir() and args.output is not None and args.output.suffix.lower() == ".jsonl":
        raise SystemExit(
            "--output must be a directory (or omitted) when --input is a directory"
        )

    try:
        input_files = iter_input_jsonl_files(args.input)
    except (FileNotFoundError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc

    if args.min_score is not None:
        selection_rule = f"score >= {args.min_score}"
    else:
        selection_rule = "highest scores (no threshold)"

    if args.per_predicted_label:
        grouping_rule = f"top {args.top_n} per predicted_label"
    else:
        grouping_rule = f"top {args.top_n} overall"

    results: list[dict[str, Any]] = []
    for input_path in input_files:
        output_path = resolve_output_path(
            input_root=args.input,
            input_path=input_path,
            top_n=args.top_n,
            per_predicted_label=args.per_predicted_label,
            output_arg=args.output,
        )
        result = process_file(
            input_path,
            output_path,
            top_n=args.top_n,
            min_score=args.min_score,
            per_predicted_label=args.per_predicted_label,
            save=args.save,
        )
        results.append(result)

        save_msg = (
            f"wrote {result['records_out']} row(s) to {display_path(output_path)}"
            if args.save
            else f"selected {result['records_out']} row(s) (not saved)"
        )
        print(
            f"{display_path(input_path)}: "
            f"read {result['records_in']} row(s); {save_msg} "
            f"across {result['labels_out']} label(s) "
            f"({grouping_rule}, {selection_rule})"
        )
        for label_id in sorted(result["per_label"]):
            print(f"  {label_id}: {result['per_label'][label_id]} row(s)")

    total_in = sum(r["records_in"] for r in results)
    total_out = sum(r["records_out"] for r in results)
    print(
        f"Done: {len(results)} file(s), {total_in} row(s) in, {total_out} row(s) out "
        f"({grouping_rule}, {selection_rule})"
    )


if __name__ == "__main__":
    main()
