"""Convert .csv files to .jsonl, writing each output beside its source.

Walks a directory tree recursively. For ``path/to/foo.csv``, writes
``path/to/foo.jsonl`` in the same folder. Each CSV row becomes one JSON object
(keys = column headers).
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def convert_file(
    csv_path: Path,
    *,
    overwrite: bool,
    delimiter: str,
    encoding: str,
) -> Path:
    out_path = csv_path.with_suffix(".jsonl")
    if out_path.exists() and not overwrite:
        if out_path.stat().st_mtime >= csv_path.stat().st_mtime:
            return out_path

    rows = 0
    with csv_path.open(newline="", encoding=encoding) as src, out_path.open(
        "w", encoding="utf-8"
    ) as dst:
        reader = csv.DictReader(src, delimiter=delimiter)
        if reader.fieldnames is None:
            raise ValueError("CSV has no header row")
        for row in reader:
            dst.write(json.dumps(row, ensure_ascii=False) + "\n")
            rows += 1

    print(f"  {display_path(csv_path)} -> {out_path.name} ({rows} rows)")
    return out_path


def find_csv_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.csv") if p.is_file())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "roots",
        nargs="*",
        type=Path,
        default=[ROOT / "data" / "raw"],
        help="Directories to scan (default: data/raw)",
    )
    parser.add_argument(
        "--delimiter",
        default=",",
        help="Column delimiter (default: comma)",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="Input file encoding (default: utf-8)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Rewrite .jsonl even when it is newer than the .csv file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List .csv files that would be converted, without writing",
    )
    args = parser.parse_args()

    total = 0
    for root in args.roots:
        root = root.resolve()
        if not root.is_dir():
            raise SystemExit(f"Not a directory: {root}")

        files = find_csv_files(root)
        if not files:
            print(f"No .csv files under {root}")
            continue

        print(f"Scanning {root} ({len(files)} file(s))")
        for csv_path in files:
            if args.dry_run:
                out_path = csv_path.with_suffix(".jsonl")
                print(f"  would convert: {display_path(csv_path)} -> {out_path.name}")
                total += 1
                continue
            try:
                convert_file(
                    csv_path,
                    overwrite=args.overwrite,
                    delimiter=args.delimiter,
                    encoding=args.encoding,
                )
            except (OSError, csv.Error, ValueError) as e:
                raise SystemExit(f"{display_path(csv_path)}: {e}") from e
            total += 1

    print(f"Done. {total} file(s) {'listed' if args.dry_run else 'processed'}.")


if __name__ == "__main__":
    main()
