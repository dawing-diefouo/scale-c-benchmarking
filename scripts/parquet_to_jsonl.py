"""Convert .parquet files to .jsonl, writing each output beside its source.

Walks a directory tree recursively. For ``path/to/foo.parquet``, writes
``path/to/foo.jsonl`` in the same folder.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def json_default(value: object) -> str:
    return str(value)


def convert_file(parquet_path: Path, *, overwrite: bool) -> Path:
    import pyarrow.parquet as pq

    out_path = parquet_path.with_suffix(".jsonl")
    if out_path.exists() and not overwrite:
        if out_path.stat().st_mtime >= parquet_path.stat().st_mtime:
            return out_path

    pf = pq.ParquetFile(parquet_path)
    rows = 0
    with out_path.open("w", encoding="utf-8") as f:
        for batch in pf.iter_batches():
            for row in batch.to_pylist():
                f.write(json.dumps(row, ensure_ascii=False, default=json_default) + "\n")
                rows += 1

    print(f"  {display_path(parquet_path)} -> {out_path.name} ({rows} rows)")
    return out_path


def find_parquet_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.parquet") if p.is_file())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "roots",
        nargs="*",
        type=Path,
        default=[ROOT / "JSONSchemaBench"],
        help="Directories to scan (default: JSONSchemaBench)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Rewrite .jsonl even when it is newer than the .parquet file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List .parquet files that would be converted, without writing",
    )
    args = parser.parse_args()

    try:
        import pyarrow.parquet  # noqa: F401
    except ImportError as e:
        raise SystemExit(
            "pyarrow is required. Install project deps: uv sync  (or: pip install pyarrow)"
        ) from e

    total = 0
    for root in args.roots:
        root = root.resolve()
        if not root.is_dir():
            raise SystemExit(f"Not a directory: {root}")

        files = find_parquet_files(root)
        if not files:
            print(f"No .parquet files under {root}")
            continue

        print(f"Scanning {root} ({len(files)} file(s))")
        for parquet_path in files:
            if args.dry_run:
                out_path = parquet_path.with_suffix(".jsonl")
                print(f"  would convert: {parquet_path} -> {out_path.name}")
                total += 1
                continue
            convert_file(parquet_path, overwrite=args.overwrite)
            total += 1

    print(f"Done. {total} file(s) {'listed' if args.dry_run else 'processed'}.")


if __name__ == "__main__":
    main()
