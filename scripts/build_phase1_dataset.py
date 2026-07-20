"""Build a curated Phase 1 benchmark dataset under ``data/phase1/``.

Scans classified Scale_C JSONL under ``data/processed/`` (one sub-folder per
upstream benchmark), groups rows by taxonomy topic
(``classification.predicted_label``), and keeps up to *N* highest-scoring rows
per (benchmark, topic). Deduplicates on record ``id`` across shards/files.

Output layout::

    data/phase1/<corpus>/
      manifest.json
      <benchmark>/
        dataset.jsonl          # all selected rows for this benchmark
        by_topic/
          <topic_id>.jsonl     # up to N rows for that topic

Edit the ``DEFAULT_*`` block or pass CLI flags. For the NLI vs embedding
views, run twice with different ``--input`` / ``--output`` roots (see
``docs/reproduce.md``).
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterator

from _top_n_by_label import (
    _TOP_N_OUTPUT_RE,
    display_path,
    iter_records,
    predicted_score,
    select_top_n,
)

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
FINAL = ROOT / "data" / "phase1"
TAXONOMY = ROOT / "schema" / "taxonomy.json"

# --- Run configuration (edit these, then: python scripts/build_phase1_dataset.py) ---
DEFAULT_INPUT = PROCESSED
DEFAULT_OUTPUT = FINAL
DEFAULT_TAXONOMY = TAXONOMY
DEFAULT_MAX_PER_TOPIC = 10
DEFAULT_SAVE = True


def is_top_n_output(path: Path) -> bool:
    return bool(_TOP_N_OUTPUT_RE.match(path.name))


def load_taxonomy_ids(path: Path) -> set[str]:
    with path.open(encoding="utf-8") as f:
        doc = json.load(f)
    labels = doc.get("labels")
    if not isinstance(labels, list):
        raise ValueError(f"{path}: expected a 'labels' array")
    ids: set[str] = set()
    for row in labels:
        if isinstance(row, dict) and isinstance(row.get("id"), str):
            ids.add(row["id"])
    if not ids:
        raise ValueError(f"{path}: no label ids found")
    return ids


def iter_processed_jsonl(
    processed_root: Path,
    *,
    exclude_benchmarks: set[str] | None = None,
) -> Iterator[tuple[str, Path]]:
    """Yield (benchmark_name, jsonl_path) for classified source files."""
    if not processed_root.is_dir():
        raise FileNotFoundError(processed_root)

    excluded = exclude_benchmarks or set()

    for path in sorted(processed_root.rglob("*.jsonl")):
        if not path.is_file() or is_top_n_output(path):
            continue
        try:
            rel = path.relative_to(processed_root)
        except ValueError:
            continue
        if not rel.parts:
            continue
        benchmark = rel.parts[0]
        if benchmark in excluded:
            continue
        yield benchmark, path


def merge_unique_by_id(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Keep one row per ``id``; on duplicates, keep the higher predicted score."""
    best: dict[str, tuple[float, dict[str, Any]]] = {}
    no_id: list[dict[str, Any]] = []

    for record in records:
        record_id = record.get("id")
        parsed = predicted_score(record)
        if not isinstance(record_id, str):
            no_id.append(record)
            continue
        if parsed is None:
            if record_id not in best:
                best[record_id] = (float("-inf"), record)
            continue
        _, score = parsed
        prev = best.get(record_id)
        if prev is None or score > prev[0]:
            best[record_id] = (score, record)

    merged = [record for _, record in best.values()]
    merged.extend(no_id)
    return merged


def build_benchmark_dataset(
    benchmark: str,
    records: list[dict[str, Any]],
    *,
    max_per_topic: int | None,
    taxonomy_ids: set[str],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    records = merge_unique_by_id(records)

    known = [
        r
        for r in records
        if (parsed := predicted_score(r)) is not None and parsed[0] in taxonomy_ids
    ]
    if max_per_topic is None:
        selected = known
    else:
        selected = select_top_n(
            known,
            top_n=max_per_topic,
            min_score=None,
            per_predicted_label=True,
        )

    per_topic: dict[str, int] = defaultdict(int)
    for record in selected:
        parsed = predicted_score(record)
        if parsed:
            per_topic[parsed[0]] += 1

    selected.sort(
        key=lambda r: (
            (predicted_score(r) or ("", 0.0))[0],
            -((predicted_score(r) or ("", 0.0))[1]),
            str(r.get("id", "")),
        )
    )
    return selected, dict(per_topic)


def write_benchmark_outputs(
    output_root: Path,
    benchmark: str,
    records: list[dict[str, Any]],
    *,
    save: bool,
) -> Path:
    bench_dir = output_root / benchmark
    by_topic_dir = bench_dir / "by_topic"
    dataset_path = bench_dir / "dataset.jsonl"

    if not save:
        return dataset_path

    bench_dir.mkdir(parents=True, exist_ok=True)
    by_topic_dir.mkdir(parents=True, exist_ok=True)

    by_topic: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        parsed = predicted_score(record)
        if parsed:
            by_topic[parsed[0]].append(record)

    with dataset_path.open("w", encoding="utf-8") as out_f:
        for record in records:
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")

    for topic_id in sorted(by_topic):
        topic_path = by_topic_dir / f"{topic_id}.jsonl"
        with topic_path.open("w", encoding="utf-8") as out_f:
            for record in by_topic[topic_id]:
                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return dataset_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Processed root with one sub-folder per benchmark (default: {DEFAULT_INPUT}).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output root for the curated dataset (default: {DEFAULT_OUTPUT}).",
    )
    parser.add_argument(
        "--taxonomy",
        type=Path,
        default=DEFAULT_TAXONOMY,
        help=f"Taxonomy JSON with label ids (default: {DEFAULT_TAXONOMY}).",
    )
    parser.add_argument(
        "--max-per-topic",
        "--top-n",
        dest="max_per_topic",
        type=int,
        default=DEFAULT_MAX_PER_TOPIC,
        help=(
            f"Max rows per topic per benchmark (default: {DEFAULT_MAX_PER_TOPIC}). "
            "Use 0 with --no-topic-cap to keep all rows."
        ),
    )
    parser.add_argument(
        "--no-topic-cap",
        action="store_true",
        help="Keep every classified row (after id dedup); ignore per-topic limits.",
    )
    parser.add_argument(
        "--exclude-benchmark",
        action="append",
        default=[],
        metavar="NAME",
        help=(
            "Skip a top-level benchmark folder or JSONL stem under --input "
            "(repeatable). Example: --exclude-benchmark qwen"
        ),
    )
    save_group = parser.add_mutually_exclusive_group()
    save_group.add_argument(
        "--save",
        dest="save",
        action="store_true",
        default=DEFAULT_SAVE,
        help="Write JSONL outputs and manifest (default).",
    )
    save_group.add_argument(
        "--no-save",
        dest="save",
        action="store_false",
        help="Only print selection stats; do not write files.",
    )
    args = parser.parse_args()

    if args.no_topic_cap:
        max_per_topic: int | None = None
    else:
        if args.max_per_topic < 1:
            raise SystemExit("--max-per-topic must be at least 1 (or pass --no-topic-cap)")
        max_per_topic = args.max_per_topic

    if not args.input.is_dir():
        raise SystemExit(f"Input directory not found: {args.input}")
    if not args.taxonomy.is_file():
        raise SystemExit(f"Taxonomy not found: {args.taxonomy}")

    taxonomy_ids = load_taxonomy_ids(args.taxonomy)
    exclude_benchmarks = set(args.exclude_benchmark)

    by_benchmark: dict[str, list[dict[str, Any]]] = defaultdict(list)
    files_per_benchmark: dict[str, int] = defaultdict(int)
    rows_read = 0

    for benchmark, path in iter_processed_jsonl(
        args.input,
        exclude_benchmarks=exclude_benchmarks,
    ):
        files_per_benchmark[benchmark] += 1
        for record in iter_records(path):
            rows_read += 1
            by_benchmark[benchmark].append(record)

    if not by_benchmark:
        raise SystemExit(f"No classified .jsonl files found under: {args.input}")

    manifest: dict[str, Any] = {
        "input": str(args.input.relative_to(ROOT))
        if args.input.is_relative_to(ROOT)
        else str(args.input),
        "taxonomy": str(args.taxonomy.relative_to(ROOT))
        if args.taxonomy.is_relative_to(ROOT)
        else str(args.taxonomy),
        "max_per_topic": max_per_topic,
        "excluded_benchmarks": sorted(exclude_benchmarks),
        "benchmarks": {},
        "totals": {
            "files_read": sum(files_per_benchmark.values()),
            "rows_read": rows_read,
            "rows_out": 0,
        },
    }

    total_out = 0
    for benchmark in sorted(by_benchmark):
        selected, per_topic = build_benchmark_dataset(
            benchmark,
            by_benchmark[benchmark],
            max_per_topic=max_per_topic,
            taxonomy_ids=taxonomy_ids,
        )
        total_out += len(selected)
        dataset_path = write_benchmark_outputs(
            args.output,
            benchmark,
            selected,
            save=args.save,
        )

        manifest["benchmarks"][benchmark] = {
            "rows_in": len(by_benchmark[benchmark]),
            "rows_out": len(selected),
            "topics_with_rows": len(per_topic),
            "per_topic": per_topic,
            "dataset": str(dataset_path.relative_to(ROOT))
            if dataset_path.is_relative_to(ROOT)
            else str(dataset_path),
        }

        save_msg = (
            f"wrote {len(selected)} row(s) to {display_path(dataset_path)}"
            if args.save
            else f"selected {len(selected)} row(s) (not saved)"
        )
        print(
            f"{benchmark}: read {len(by_benchmark[benchmark])} row(s) "
            f"from {files_per_benchmark[benchmark]} file(s); {save_msg} "
            f"across {len(per_topic)} topic(s)"
            + (
                " (no per-topic cap)"
                if max_per_topic is None
                else f" (max {max_per_topic} per topic)"
            )
        )
        for topic_id in sorted(per_topic):
            print(f"  {topic_id}: {per_topic[topic_id]} row(s)")

    manifest["totals"]["rows_out"] = total_out
    manifest["totals"]["benchmarks"] = len(by_benchmark)

    if args.save:
        args.output.mkdir(parents=True, exist_ok=True)
        manifest_path = args.output / "manifest.json"
        with manifest_path.open("w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"Wrote manifest to {display_path(manifest_path)}")

    print(
        f"Done: {len(by_benchmark)} benchmark(s), {rows_read} row(s) in, "
        f"{total_out} row(s) out"
        + (
            " (no per-topic cap)"
            if max_per_topic is None
            else f" (max {max_per_topic} per topic per benchmark)"
        )
    )


if __name__ == "__main__":
    main()
