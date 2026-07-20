#!/usr/bin/env python3
"""Convert .json / .csv / .parquet files to .jsonl beside each source.

Walks one or more directory trees. By default converts all supported formats
under ``data/raw/``.

Examples::

    python scripts/convert_to_jsonl.py
    python scripts/convert_to_jsonl.py data/raw/huggingface/CyberMetric
    python scripts/convert_to_jsonl.py --format parquet data/raw
    python scripts/convert_to_jsonl.py --dry-run
"""

from __future__ import annotations

import argparse
import csv
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = ROOT / "data" / "raw"
FORMATS = ("json", "csv", "parquet")


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def json_default(value: object) -> str:
    return str(value)


def should_skip(src: Path, out: Path, *, overwrite: bool) -> bool:
    if overwrite or not out.exists():
        return False
    return out.stat().st_mtime >= src.stat().st_mtime


def iter_json_records(
    data: Any,
    *,
    array_key: str | None,
    auto_array_key: bool,
) -> Iterator[Any]:
    if isinstance(data, list):
        yield from data
        return
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON array or object, got {type(data).__name__}")
    if array_key is not None:
        if array_key not in data:
            raise ValueError(f"missing array key {array_key!r}")
        items = data[array_key]
        if not isinstance(items, list):
            raise ValueError(f"{array_key!r} is not a JSON array")
        yield from items
        return
    if auto_array_key:
        list_keys = [key for key, value in data.items() if isinstance(value, list)]
        if len(list_keys) == 1:
            yield from data[list_keys[0]]
            return
    yield data


def convert_json(
    path: Path,
    *,
    overwrite: bool,
    array_key: str | None,
    auto_array_key: bool,
) -> int:
    out = path.with_suffix(".jsonl")
    if should_skip(path, out, overwrite=overwrite):
        return 0
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = 0
    with out.open("w", encoding="utf-8") as f:
        for row in iter_json_records(data, array_key=array_key, auto_array_key=auto_array_key):
            f.write(json.dumps(row, ensure_ascii=False, default=json_default) + "\n")
            rows += 1
    print(f"  {display_path(path)} -> {out.name} ({rows} rows)")
    return 1


def convert_csv(
    path: Path,
    *,
    overwrite: bool,
    delimiter: str,
    encoding: str,
) -> int:
    out = path.with_suffix(".jsonl")
    if should_skip(path, out, overwrite=overwrite):
        return 0
    rows = 0
    with path.open(newline="", encoding=encoding) as src, out.open("w", encoding="utf-8") as dst:
        reader = csv.DictReader(src, delimiter=delimiter)
        if reader.fieldnames is None:
            raise ValueError("CSV has no header row")
        for row in reader:
            dst.write(json.dumps(row, ensure_ascii=False) + "\n")
            rows += 1
    print(f"  {display_path(path)} -> {out.name} ({rows} rows)")
    return 1


def convert_parquet(path: Path, *, overwrite: bool) -> int:
    import pyarrow.parquet as pq

    out = path.with_suffix(".jsonl")
    if should_skip(path, out, overwrite=overwrite):
        return 0
    pf = pq.ParquetFile(path)
    rows = 0
    with out.open("w", encoding="utf-8") as f:
        for batch in pf.iter_batches():
            for row in batch.to_pylist():
                f.write(json.dumps(row, ensure_ascii=False, default=json_default) + "\n")
                rows += 1
    print(f"  {display_path(path)} -> {out.name} ({rows} rows)")
    return 1


def find_files(root: Path, fmt: str) -> list[Path]:
    return sorted(p for p in root.rglob(f"*.{fmt}") if p.is_file())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "roots",
        nargs="*",
        type=Path,
        default=[DEFAULT_ROOT],
        help="Directories to scan (default: data/raw)",
    )
    parser.add_argument(
        "--format",
        choices=(*FORMATS, "all"),
        default="all",
        help="Which source format to convert (default: all)",
    )
    parser.add_argument("--array-key", metavar="KEY", help="JSON: unwrap this list field")
    parser.add_argument(
        "--auto-array-key",
        action="store_true",
        default=True,
        help="JSON: expand sole list field in a top-level object (default: on)",
    )
    parser.add_argument(
        "--no-auto-array-key",
        action="store_false",
        dest="auto_array_key",
        help="JSON: write the top-level object as one line",
    )
    parser.add_argument("--delimiter", default=",", help="CSV delimiter (default: comma)")
    parser.add_argument("--encoding", default="utf-8", help="CSV encoding (default: utf-8)")
    parser.add_argument("--overwrite", action="store_true", help="Rewrite existing .jsonl files")
    parser.add_argument("--dry-run", action="store_true", help="List files without writing")
    args = parser.parse_args()

    formats = list(FORMATS) if args.format == "all" else [args.format]
    if "parquet" in formats:
        try:
            import pyarrow.parquet  # noqa: F401
        except ImportError as e:
            raise SystemExit(
                "pyarrow is required for parquet. Install deps: uv sync"
            ) from e

    total = 0
    for root in args.roots:
        root = root.resolve()
        if not root.is_dir():
            raise SystemExit(f"Not a directory: {root}")

        for fmt in formats:
            files = find_files(root, fmt)
            if not files:
                continue
            print(f"Scanning {root} for .{fmt} ({len(files)} file(s))")
            for path in files:
                if args.dry_run:
                    print(f"  would convert: {display_path(path)} -> {path.with_suffix('.jsonl').name}")
                    total += 1
                    continue
                try:
                    if fmt == "json":
                        total += convert_json(
                            path,
                            overwrite=args.overwrite,
                            array_key=args.array_key,
                            auto_array_key=args.auto_array_key,
                        )
                    elif fmt == "csv":
                        total += convert_csv(
                            path,
                            overwrite=args.overwrite,
                            delimiter=args.delimiter,
                            encoding=args.encoding,
                        )
                    else:
                        total += convert_parquet(path, overwrite=args.overwrite)
                except (OSError, ValueError, json.JSONDecodeError, csv.Error) as e:
                    raise SystemExit(f"{display_path(path)}: {e}") from e

    print(f"Done. {total} file(s) {'listed' if args.dry_run else 'processed'}.")


if __name__ == "__main__":
    main()
