"""Convert .json files to .jsonl, writing each output beside its source.

Walks a directory tree recursively. For ``path/to/foo.json``, writes
``path/to/foo.jsonl`` in the same folder.

Supports:
- a top-level JSON array (one line per element);
- a top-level object with a list field (use ``--array-key`` or ``--auto-array-key``);
- a single top-level object (one line).
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def json_default(value: object) -> str:
    return str(value)


def iter_records(
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


def convert_file(
    json_path: Path,
    *,
    overwrite: bool,
    array_key: str | None,
    auto_array_key: bool,
) -> Path:
    out_path = json_path.with_suffix(".jsonl")
    if out_path.exists() and not overwrite:
        if out_path.stat().st_mtime >= json_path.stat().st_mtime:
            return out_path

    data = json.loads(json_path.read_text(encoding="utf-8"))
    rows = 0
    with out_path.open("w", encoding="utf-8") as f:
        for row in iter_records(data, array_key=array_key, auto_array_key=auto_array_key):
            f.write(json.dumps(row, ensure_ascii=False, default=json_default) + "\n")
            rows += 1

    print(f"  {display_path(json_path)} -> {out_path.name} ({rows} rows)")
    return out_path


def find_json_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.json") if p.is_file())


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
        "--array-key",
        metavar="KEY",
        help="Unwrap this list field from a top-level object (e.g. questions)",
    )
    parser.add_argument(
        "--auto-array-key",
        action="store_true",
        default=True,
        help="If the root is an object with exactly one list field, expand it (default: on)",
    )
    parser.add_argument(
        "--no-auto-array-key",
        action="store_false",
        dest="auto_array_key",
        help="Write the top-level object as a single JSONL line",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Rewrite .jsonl even when it is newer than the .json file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List .json files that would be converted, without writing",
    )
    args = parser.parse_args()

    total = 0
    for root in args.roots:
        root = root.resolve()
        if not root.is_dir():
            raise SystemExit(f"Not a directory: {root}")

        files = find_json_files(root)
        if not files:
            print(f"No .json files under {root}")
            continue

        print(f"Scanning {root} ({len(files)} file(s))")
        for json_path in files:
            if args.dry_run:
                out_path = json_path.with_suffix(".jsonl")
                print(f"  would convert: {display_path(json_path)} -> {out_path.name}")
                total += 1
                continue
            try:
                convert_file(
                    json_path,
                    overwrite=args.overwrite,
                    array_key=args.array_key,
                    auto_array_key=args.auto_array_key,
                )
            except (json.JSONDecodeError, ValueError) as e:
                raise SystemExit(f"{display_path(json_path)}: {e}") from e
            total += 1

    print(f"Done. {total} file(s) {'listed' if args.dry_run else 'processed'}.")


if __name__ == "__main__":
    main()
