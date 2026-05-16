"""Select top-N classified rows per predicted label above a score threshold.

Reads Scale_C JSONL records (see ``schema/schema.json``), keeps rows whose
score for ``classification.predicted_label`` exceeds the min-score threshold,
then writes up to N highest-scoring rows per label to ``data/processed/``.
Edit the ``DEFAULT_*`` run configuration block at the top of this file, then run
with no CLI arguments; flags still override those defaults.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

# --- Run configuration (edit these, then: python scripts/top_n_by_label.py) ---
DEFAULT_INPUT = PROCESSED / "classified_mmlu_ccs_.jsonl"
DEFAULT_OUTPUT = PROCESSED / "classified_top_n.jsonl"
DEFAULT_TOP_N = 10
DEFAULT_MIN_SCORE = 0.5


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
    min_score: float,
) -> list[dict[str, Any]]:
    by_label: dict[str, list[tuple[float, dict[str, Any]]]] = defaultdict(list)

    for record in records:
        parsed = predicted_score(record)
        if parsed is None:
            continue
        pred_id, score = parsed
        if score <= min_score:
            continue
        by_label[pred_id].append((score, record))

    selected: list[tuple[float, str, dict[str, Any]]] = []
    for pred_id, scored in by_label.items():
        scored.sort(key=lambda item: item[0], reverse=True)
        for score, record in scored[:top_n]:
            selected.append((score, pred_id, record))

    selected.sort(key=lambda item: (item[1], -item[0]))
    return [record for _, _, record in selected]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Classified JSONL (default: {DEFAULT_INPUT}).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Filtered JSONL (default: {DEFAULT_OUTPUT}).",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=DEFAULT_TOP_N,
        help=f"Maximum rows per predicted_label (default: {DEFAULT_TOP_N}).",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=DEFAULT_MIN_SCORE,
        help=f"Drop rows with predicted-label score <= this (default: {DEFAULT_MIN_SCORE}).",
    )
    args = parser.parse_args()

    if args.top_n < 1:
        raise SystemExit("--top-n must be at least 1")
    if not (0.0 <= args.min_score <= 1.0):
        raise SystemExit("--min-score must be between 0 and 1")
    if not args.input.is_file():
        raise SystemExit(f"Input not found: {args.input}")

    records = list(iter_records(args.input))
    kept = select_top_n(records, top_n=args.top_n, min_score=args.min_score)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as out_f:
        for record in kept:
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")

    labels_in = len({predicted_score(r)[0] for r in records if predicted_score(r)})
    labels_out = len({predicted_score(r)[0] for r in kept if predicted_score(r)})
    print(
        f"Read {len(records)} row(s) from {display_path(args.input)}; "
        f"wrote {len(kept)} row(s) across {labels_out} label(s) "
        f"(top {args.top_n} per label, score > {args.min_score}) "
        f"to {display_path(args.output)} "
        f"[{labels_in} label(s) in input]"
    )


if __name__ == "__main__":
    main()
