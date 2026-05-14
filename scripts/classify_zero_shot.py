"""Zero-shot classification with MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7.

Reads label names from ``schema/taxonomy.json``, runs the Hugging Face
``zero-shot-classification`` pipeline (see model card), and appends one JSON
object per input line to ``data/processed/classified.jsonl``.

Model: https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema" / "taxonomy.json"
PROCESSED = ROOT / "data" / "processed"
DEFAULT_OUT = PROCESSED / "classified_mmlu.jsonl"

DEFAULT_MODEL = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"


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


def format_mmlu_text(row: dict) -> str:
    q = row.get("question") or ""
    choices = row.get("choices") or []
    if not choices:
        return q
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    lines = [q.strip(), "", "Choices:"]
    for i, c in enumerate(choices):
        pref = letters[i] if i < len(letters) else str(i)
        lines.append(f"  {pref}) {c}")
    return "\n".join(lines)


def iter_jsonl(path: Path):
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            yield line_no, json.loads(line)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "data" / "raw" / "huggingface" / "mmlu" / "computer_security" / "test.jsonl",
        help="JSONL file with MMLU-style rows (question, choices, answer, subject, ...).",
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
        help="Append-only JSONL with predictions (set --truncate to overwrite).",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="HF model id for zero-shot-classification.",
    )
    parser.add_argument(
        "--multi-label",
        action="store_true",
        help="If set, allow multiple labels above 0.5 * top score (same semantics as HF multi_label).",
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
        help="Process at most this many non-empty JSONL rows (after --start).",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=0,
        help="Skip the first N non-empty JSONL rows.",
    )
    args = parser.parse_args()

    if not args.input.is_file():
        raise SystemExit(
            f"Input not found: {args.input}\n"
            "Fetch data first (e.g. change fetch_datasets HF_SUBSET to computer_security) "
            "or pass --input to an existing JSONL."
        )
    if not args.taxonomy.is_file():
        raise SystemExit(f"Taxonomy not found: {args.taxonomy}")

    candidate_names, name_to_id = load_taxonomy(args.taxonomy)
    ids_in_order = [name_to_id[n] for n in candidate_names]

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
    source_hint = str(args.input.relative_to(ROOT)) if args.input.is_relative_to(ROOT) else str(args.input)

    with args.output.open(mode, encoding="utf-8") as out_f:
        for line_no, row in iter_jsonl(args.input):
            text = format_mmlu_text(row)
            if args.start > 0 and seen < args.start:
                seen += 1
                continue
            if args.max_rows is not None and written >= args.max_rows:
                break

            result = classifier(
                text,
                candidate_names,
                multi_label=args.multi_label,
            )

            labels_out = result["labels"]
            scores_out = result["scores"]
            id_scores = {
                name_to_id[name]: float(score) for name, score in zip(labels_out, scores_out, strict=True)
            }
            top_name = labels_out[0]
            pred_id = name_to_id[top_name]

            sample_id = f"{row.get('subject', 'unknown')}:{line_no}"
            record = {
                "id": sample_id,
                "source": source_hint,
                "text": text,
                "predicted_label": pred_id,
                "predicted_label_name": top_name,
                "raw_scores": id_scores,
                "label_ids": ids_in_order,
                "mmlu_answer_index": row.get("answer"),
            }
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
            seen += 1
            written += 1

    print(
        f"Wrote {written} row(s) to {args.output.relative_to(ROOT) if args.output.is_relative_to(ROOT) else args.output} "
        f"(model={args.model}, device={device})"
    )


if __name__ == "__main__":
    main()
