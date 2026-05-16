"""Extract JSONL rows whose question text contains cloze blanks (``_____``).

Scans a directory tree (default: cyberbench) for ``.jsonl`` files, keeps rows
where any configured question field contains the cloze marker, and writes each
source file's matches to ``data/raw/custom/custom_<name>.jsonl``.

Edit the ``DEFAULT_*`` globals below, then run with no CLI arguments; flags
still override those defaults.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
CUSTOM = RAW / "custom"

# --- Run configuration (edit these, then: python scripts/extract_cloze_questions.py) ---
DEFAULT_INPUT_DIR = RAW / "huggingface" / "CyberMetric"
DEFAULT_OUTPUT_DIR = CUSTOM
DEFAULT_OUTPUT_PREFIX = "custom_"
DEFAULT_CLOZE_MARKER = "___"
DEFAULT_QUESTION_KEYS = ("question",)
DEFAULT_RECURSIVE = True
DEFAULT_DRY_RUN = False
DEFAULT_OVERWRITE = True


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def find_jsonl_files(root: Path, *, recursive: bool) -> list[Path]:
    if root.is_file():
        if root.suffix.lower() != ".jsonl":
            raise ValueError(f"Expected a .jsonl file, got: {root}")
        return [root]
    if not root.is_dir():
        raise FileNotFoundError(root)
    pattern = "**/*.jsonl" if recursive else "*.jsonl"
    return sorted(p for p in root.glob(pattern) if p.is_file())


def output_name_for(
    source: Path,
    scan_root: Path,
    *,
    prefix: str,
) -> str:
    try:
        rel = source.relative_to(scan_root)
        stem = rel.with_suffix("").as_posix().replace("/", "_")
    except ValueError:
        stem = source.with_suffix("").name
    return f"{prefix}{stem}.jsonl"


def row_has_cloze_question(
    row: dict[str, Any],
    *,
    question_keys: tuple[str, ...],
    cloze_marker: str,
) -> bool:
    for key in question_keys:
        value = row.get(key)
        if isinstance(value, str) and cloze_marker in value:
            return True
    return False


def iter_rows(path: Path) -> Iterator[tuple[int, dict[str, Any]]]:
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{display_path(path)}:{line_no}: invalid JSON") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{display_path(path)}:{line_no}: expected a JSON object")
            yield line_no, row


def extract_file(
    source: Path,
    scan_root: Path,
    *,
    output_dir: Path,
    output_prefix: str,
    question_keys: tuple[str, ...],
    cloze_marker: str,
    overwrite: bool,
    dry_run: bool,
) -> tuple[Path, int, int]:
    out_name = output_name_for(source, scan_root, prefix=output_prefix)
    out_path = output_dir / out_name

    kept = 0
    total = 0
    if dry_run:
        for _, row in iter_rows(source):
            total += 1
            if row_has_cloze_question(
                row, question_keys=question_keys, cloze_marker=cloze_marker
            ):
                kept += 1
        return out_path, kept, total

    output_dir.mkdir(parents=True, exist_ok=True)
    if out_path.exists() and not overwrite:
        raise FileExistsError(f"Output exists (use --overwrite): {out_path}")

    with out_path.open("w", encoding="utf-8") as out_f:
        for _, row in iter_rows(source):
            total += 1
            if not row_has_cloze_question(
                row, question_keys=question_keys, cloze_marker=cloze_marker
            ):
                continue
            out_f.write(json.dumps(row, ensure_ascii=False) + "\n")
            kept += 1

    return out_path, kept, total


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help=f"Directory or .jsonl file to scan (default: {DEFAULT_INPUT_DIR}).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory for custom_*.jsonl outputs (default: {DEFAULT_OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--output-prefix",
        default=DEFAULT_OUTPUT_PREFIX,
        help=f"Output filename prefix (default: {DEFAULT_OUTPUT_PREFIX!r}).",
    )
    parser.add_argument(
        "--cloze-marker",
        default=DEFAULT_CLOZE_MARKER,
        help=f"Substring marking cloze blanks (default: {DEFAULT_CLOZE_MARKER!r}).",
    )
    parser.add_argument(
        "--question-keys",
        nargs="+",
        default=list(DEFAULT_QUESTION_KEYS),
        help=f"Row keys treated as question text (default: {', '.join(DEFAULT_QUESTION_KEYS)}).",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Only scan .jsonl files directly under --input-dir (not subfolders).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=DEFAULT_DRY_RUN,
        help="Report matches without writing output files.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=DEFAULT_OVERWRITE,
        help="Replace existing custom_*.jsonl outputs.",
    )
    args = parser.parse_args()

    input_dir = args.input_dir.resolve()
    output_dir = args.output_dir.resolve()
    question_keys = tuple(args.question_keys)
    recursive = not args.no_recursive

    if not args.cloze_marker:
        raise SystemExit("--cloze-marker must not be empty")
    if not question_keys:
        raise SystemExit("--question-keys must list at least one field name")

    scan_root = input_dir if input_dir.is_dir() else input_dir.parent
    files = find_jsonl_files(input_dir, recursive=recursive)
    if not files:
        raise SystemExit(f"No .jsonl files under {input_dir}")

    print(
        f"Scanning {display_path(input_dir)} ({len(files)} file(s)); "
        f"cloze marker {args.cloze_marker!r} in keys {list(question_keys)}"
    )

    grand_kept = 0
    grand_total = 0
    written = 0
    for source in files:
        try:
            out_path, kept, total = extract_file(
                source,
                scan_root,
                output_dir=output_dir,
                output_prefix=args.output_prefix,
                question_keys=question_keys,
                cloze_marker=args.cloze_marker,
                overwrite=args.overwrite,
                dry_run=args.dry_run,
            )
        except (OSError, ValueError) as exc:
            raise SystemExit(f"{display_path(source)}: {exc}") from exc

        grand_kept += kept
        grand_total += total
        if kept:
            written += 1
            action = "would write" if args.dry_run else "wrote"
            print(
                f"  {action} {kept}/{total} row(s) -> "
                f"{display_path(out_path)} from {display_path(source)}"
            )

    suffix = "listed" if args.dry_run else "written"
    print(
        f"Done. {grand_kept}/{grand_total} matching row(s) across "
        f"{written} file(s) {suffix} under {display_path(output_dir)}."
    )


if __name__ == "__main__":
    main()
