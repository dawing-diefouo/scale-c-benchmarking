"""Build an MCQ-only classification gold standard (schema v2 + reason).

Samples existing multiple-choice questions from configured processed datasets
(default: CyberMetric and mmlu/computer_security), skips cloze / fill-in-blank
items, classifies each candidate's cyber topic via an OpenRouter frontier model
with a short reason, and keeps up to *count* rows whose label is not
``SCLC02801`` (Other).

Outputs:

* ``data/gold_standard/gold_standard_mcq_100.jsonl`` — Scale_C records per
  ``schema/schema.json``, plus ``reference`` and ``classification.reason``.
* ``data/gold_standard/gold_standard_mcq_100.csv`` — flat review sheet.

Edit the ``DEFAULT_*`` block or pass CLI flags.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
GOLD = ROOT / "data" / "gold_standard"
RAW = ROOT / "data" / "raw" / "huggingface"
TAXONOMY_PATH = ROOT / "schema" / "taxonomy.json"

_QWEN_COMBINED = PROCESSED / "qwen_combined"
if not _QWEN_COMBINED.is_dir():
    _archived = ROOT / "_archive" / "data_processed_qwen_combined"
    if _archived.is_dir():
        _QWEN_COMBINED = _archived

DEFAULT_DATASETS = (
    _QWEN_COMBINED / "CyberMetric",
    _QWEN_COMBINED / "mmlu" / "computer_security",
)
DEFAULT_OUTPUT_JSONL = GOLD / "gold_standard_mcq_100.jsonl"
DEFAULT_OUTPUT_CSV = GOLD / "gold_standard_mcq_100.csv"
DEFAULT_COUNT = 100
DEFAULT_SEED = 42
DEFAULT_MODEL = "anthropic/claude-sonnet-4.6"
DEFAULT_API_BASE = "https://openrouter.ai/api"
OTHER_LABEL = "SCLC02801"

CLOZE_RE = re.compile(r"_{3,}|\.{3,}")
JSON_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)


@dataclass(frozen=True)
class TaxonomyEntry:
    id: str
    name: str
    description: str


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def load_taxonomy(path: Path) -> list[TaxonomyEntry]:
    with path.open(encoding="utf-8") as handle:
        doc = json.load(handle)
    entries: list[TaxonomyEntry] = []
    for row in doc.get("labels", []):
        if not isinstance(row, dict):
            continue
        label_id = row.get("id")
        name = row.get("name")
        if isinstance(label_id, str) and isinstance(name, str):
            entries.append(
                TaxonomyEntry(
                    id=label_id,
                    name=name,
                    description=str(row.get("description") or ""),
                )
            )
    if not entries:
        raise ValueError(f"{path}: no taxonomy labels found")
    return entries


def iter_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def is_cloze_question(question: str) -> bool:
    return bool(CLOZE_RE.search(question or ""))


def is_mcq_record(record: dict[str, Any]) -> bool:
    payload = record.get("payload")
    if not isinstance(payload, dict):
        return False
    question = payload.get("question")
    if not isinstance(question, str) or not question.strip():
        return False
    if is_cloze_question(question):
        return False
    if record.get("task_type") == "mcq_answering":
        return True
    if isinstance(payload.get("answers"), dict) and len(payload["answers"]) >= 2:
        return True
    if isinstance(payload.get("choices"), list) and len(payload["choices"]) >= 2:
        return True
    if payload.get("option_a") is not None:
        return True
    return False


def normalize_question(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def processed_to_raw_path(processed_file: Path) -> Path | None:
    rel: Path | None = None
    for prefix in (
        PROCESSED / "qwen_combined",
        PROCESSED / "qwen_1",
        PROCESSED / "qwen",
        PROCESSED,
    ):
        try:
            rel = processed_file.relative_to(prefix)
            break
        except ValueError:
            continue
    if rel is None:
        return None
    return RAW / rel


def extract_raw_question(row: dict[str, Any]) -> str | None:
    question = row.get("question")
    if isinstance(question, str) and question.strip():
        return question.strip()
    return None


def build_raw_question_index(raw_paths: list[Path]) -> dict[str, tuple[str, int]]:
    index: dict[str, tuple[str, int]] = {}
    for raw_path in raw_paths:
        if not raw_path.is_file():
            continue
        source = display_path(raw_path)
        for line_no, row in enumerate(iter_jsonl(raw_path), start=1):
            question = extract_raw_question(row)
            if question:
                index.setdefault(normalize_question(question), (source, line_no))
    return index


def index_to_letter(index: int) -> str | None:
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if 0 <= index < len(letters):
        return letters[index]
    return None


def normalize_choices(payload: dict[str, Any]) -> dict[str, str]:
    answers = payload.get("answers")
    if isinstance(answers, dict) and answers:
        return {str(key).upper(): str(value) for key, value in answers.items()}

    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        return {
            (letters[i] if i < len(letters) else str(i)): str(choice)
            for i, choice in enumerate(choices)
        }

    out: dict[str, str] = {}
    for letter in "abcdefghijklmnopqrstuvwxyz":
        key = f"option_{letter}"
        if key in payload and payload[key] is not None:
            out[letter.upper()] = str(payload[key])
    return out


def normalize_correct_answer(payload: dict[str, Any], choices: dict[str, str]) -> str | None:
    evaluation = payload.get("evaluation")
    if isinstance(evaluation, dict):
        answer = evaluation.get("correct_answer")
        if isinstance(answer, str) and answer.strip():
            return answer.strip().upper()
        if isinstance(answer, dict) and answer:
            for letter, text in answer.items():
                if str(letter).upper() in choices:
                    return str(letter).upper()

    for key in ("solution", "answer"):
        value = payload.get(key)
        if isinstance(value, int):
            letter = index_to_letter(value)
            if letter:
                return letter
        if isinstance(value, str) and value.strip():
            stripped = value.strip().upper()
            if stripped in choices:
                return stripped
            if len(stripped) == 1 and stripped in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                return stripped
    return None


def normalize_payload(record: dict[str, Any]) -> dict[str, Any]:
    raw_payload = record.get("payload")
    if not isinstance(raw_payload, dict):
        raise ValueError(f"Record {record.get('id')} has no payload")
    choices = normalize_choices(raw_payload)
    question = str(raw_payload.get("question") or "").strip()
    return {"question": question, "choices": choices}


def normalize_evaluation(record: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any] | None:
    existing = record.get("evaluation")
    if isinstance(existing, dict) and existing.get("correct_answer") is not None:
        answer = existing["correct_answer"]
        if isinstance(answer, dict):
            for letter in answer:
                if str(letter).upper() in payload["choices"]:
                    return {
                        "scoring_type": existing.get("scoring_type", "exact_match"),
                        "correct_answer": str(letter).upper(),
                        "max_score": existing.get("max_score", 1),
                    }
        if isinstance(answer, str):
            return {
                "scoring_type": existing.get("scoring_type", "exact_match"),
                "correct_answer": answer.strip().upper(),
                "max_score": existing.get("max_score", 1),
            }

    correct = normalize_correct_answer(record.get("payload") or {}, payload["choices"])
    if correct is None:
        return None
    return {"scoring_type": "exact_match", "correct_answer": correct, "max_score": 1}


def resolve_reference(
    record: dict[str, Any],
    processed_file: Path,
    raw_index: dict[str, tuple[str, int]],
) -> dict[str, Any]:
    payload = record.get("payload") or {}
    question = str(payload.get("question") or "").strip()
    raw_path = processed_to_raw_path(processed_file)
    source_file = ""
    line_no: int | None = None
    if question:
        hit = raw_index.get(normalize_question(question))
        if hit:
            source_file, line_no = hit
    if not source_file and raw_path is not None:
        source_file = display_path(raw_path)
    rel_parts = processed_file.relative_to(PROCESSED).parts
    if "computer_security" in rel_parts:
        dataset = "mmlu/computer_security"
    elif "CyberMetric" in rel_parts:
        dataset = "CyberMetric"
    elif len(rel_parts) >= 2:
        dataset = "/".join(rel_parts[:2])
    else:
        dataset = rel_parts[0] if rel_parts else ""
    ref: dict[str, Any] = {
        "dataset": dataset,
        "processed_file": display_path(processed_file),
        "source_file": source_file,
        "original_id": record.get("id", ""),
    }
    if line_no is not None:
        ref["source_line_no"] = line_no
    subject = payload.get("subject")
    if isinstance(subject, str) and subject.strip():
        ref["subject"] = subject.strip()
    sample_id = payload.get("sample_id")
    if isinstance(sample_id, str) and sample_id.strip():
        ref["sample_id"] = sample_id.strip()
    return ref


def classification_prompt(question: str, choices: dict[str, str], entries: list[TaxonomyEntry]) -> str:
    options = "\n".join(
        f"- {entry.id}: {entry.name} — {entry.description}"
        for entry in entries
    )
    choice_lines = "\n".join(f"{letter}) {text}" for letter, text in sorted(choices.items()))
    return (
        "You classify cybersecurity multiple-choice questions into exactly one Scale_C topic label.\n"
        "Reply with JSON only (no markdown), using keys:\n"
        '  "predicted_label" (taxonomy id, e.g. SCLC00701),\n'
        '  "predicted_label_name" (exact label name from the list),\n'
        '  "reason" (one short sentence, max 25 words, why this label fits).\n'
        "Use SCLC02801 (Other) only when the question is clearly outside cybersecurity.\n\n"
        f"Allowed labels:\n{options}\n\n"
        f"Question:\n{question}\n\n"
        f"Choices:\n{choice_lines}\n"
    )


def parse_classification_response(text: str) -> dict[str, str]:
    stripped = text.strip()
    match = JSON_FENCE_RE.search(stripped)
    if match:
        stripped = match.group(1).strip()
    data = json.loads(stripped)
    if not isinstance(data, dict):
        raise ValueError("classification response is not a JSON object")
    return {
        "predicted_label": str(data.get("predicted_label") or "").strip(),
        "predicted_label_name": str(data.get("predicted_label_name") or "").strip(),
        "reason": str(data.get("reason") or "").strip(),
    }


class FrontierClassifier:
    def __init__(
        self,
        *,
        model: str,
        api_base_url: str,
        api_key: str,
        entries: list[TaxonomyEntry],
    ) -> None:
        self.model = model
        self.api_base_url = api_base_url.rstrip("/")
        self.api_key = api_key
        self.entries = entries
        self.by_id = {entry.id: entry for entry in entries}
        self.by_name = {entry.name.casefold(): entry for entry in entries}

    def classify(self, question: str, choices: dict[str, str]) -> dict[str, str]:
        prompt = classification_prompt(question, choices, self.entries)
        request = urllib.request.Request(
            f"{self.api_base_url}/v1/chat/completions",
            data=json.dumps(
                {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 256,
                    "temperature": 0,
                }
            ).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenRouter request failed ({exc.code}): {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"OpenRouter unreachable: {exc.reason}") from exc

        content = body["choices"][0]["message"]["content"].strip()
        parsed = parse_classification_response(content)
        label_id = parsed["predicted_label"]
        label_name = parsed["predicted_label_name"]
        entry = self.by_id.get(label_id)
        if entry is None and label_name:
            entry = self.by_name.get(label_name.casefold())
        if entry is not None:
            label_id = entry.id
            label_name = entry.name
        if not label_id or not label_name:
            raise ValueError(f"Could not resolve label from model response: {content!r}")
        parsed["predicted_label"] = label_id
        parsed["predicted_label_name"] = label_name
        return parsed


def dry_run_classification(record: dict[str, Any]) -> dict[str, str]:
    cls = record.get("classification") or {}
    label_id = str(cls.get("predicted_label") or OTHER_LABEL)
    label_name = str(cls.get("predicted_label_name") or "Other")
    reason = str(cls.get("reason") or "Dry-run: reused existing processed classification")
    return {
        "predicted_label": label_id,
        "predicted_label_name": label_name,
        "reason": reason,
    }


def collect_candidates(dataset_roots: list[Path]) -> list[tuple[dict[str, Any], Path]]:
    candidates: list[tuple[dict[str, Any], Path]] = []
    seen_questions: set[str] = set()
    for root in dataset_roots:
        if not root.is_dir():
            print(f"Warning: dataset root missing: {display_path(root)}", file=sys.stderr)
            continue
        for path in sorted(root.rglob("*.jsonl")):
            if "top_n" in path.name:
                continue
            for record in iter_jsonl(path):
                if not is_mcq_record(record):
                    continue
                question = normalize_question(str((record.get("payload") or {}).get("question") or ""))
                if not question or question in seen_questions:
                    continue
                seen_questions.add(question)
                candidates.append((record, path))
    return candidates


def build_gold_record(
    *,
    gold_id: str,
    source: dict[str, Any],
    processed_file: Path,
    classification: dict[str, str],
    model: str,
    raw_index: dict[str, tuple[str, int]],
) -> dict[str, Any]:
    payload = normalize_payload(source)
    metadata = dict(source.get("metadata") or {})
    metadata.setdefault("difficulty", metadata.get("difficulty") or "-")
    metadata.setdefault("risk_category", metadata.get("risk_category") or "-")
    metadata.setdefault("cognitive_skill", metadata.get("cognitive_skill") or "-")
    metadata.setdefault("language", metadata.get("language") or "en")
    metadata.setdefault("source", metadata.get("source") or display_path(processed_file.parent))

    record: dict[str, Any] = {
        "id": gold_id,
        "benchmark": "scale_c",
        "version": 2,
        "tier": source.get("tier", 1),
        "task_type": "mcq_answering",
        "metadata": metadata,
        "classification": {
            "predicted_label": classification["predicted_label"],
            "predicted_label_name": classification["predicted_label_name"],
            "reason": classification["reason"],
            "raw_scores": {},
            "classifier": {"backend": "openrouter", "model": model},
        },
        "payload": payload,
        "reference": resolve_reference(source, processed_file, raw_index),
    }
    evaluation = normalize_evaluation(source, payload)
    if evaluation is not None:
        record["evaluation"] = evaluation
    return record


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def choices_to_cell(choices: dict[str, str]) -> str:
    return " | ".join(f"{letter}) {text}" for letter, text in sorted(choices.items()))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "id",
        "dataset",
        "source_file",
        "source_line_no",
        "processed_file",
        "original_id",
        "question",
        "choices",
        "correct_answer",
        "predicted_label",
        "predicted_label_name",
        "reason",
        "classifier_model",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            ref = row.get("reference") or {}
            payload = row.get("payload") or {}
            cls = row.get("classification") or {}
            evaluation = row.get("evaluation") or {}
            writer.writerow(
                {
                    "id": row.get("id", ""),
                    "dataset": ref.get("dataset", ""),
                    "source_file": ref.get("source_file", ""),
                    "source_line_no": ref.get("source_line_no", ""),
                    "processed_file": ref.get("processed_file", ""),
                    "original_id": ref.get("original_id", ""),
                    "question": payload.get("question", ""),
                    "choices": choices_to_cell(payload.get("choices") or {}),
                    "correct_answer": evaluation.get("correct_answer", ""),
                    "predicted_label": cls.get("predicted_label", ""),
                    "predicted_label_name": cls.get("predicted_label_name", ""),
                    "reason": cls.get("reason", ""),
                    "classifier_model": (cls.get("classifier") or {}).get("model", ""),
                }
            )


def load_existing_ids(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    return {str(row.get("id")) for row in iter_jsonl(path) if row.get("id")}


def load_existing_questions(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    questions: set[str] = set()
    for row in iter_jsonl(path):
        payload = row.get("payload") or {}
        question = payload.get("question")
        if isinstance(question, str):
            questions.add(normalize_question(question))
    return questions


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--datasets",
        type=Path,
        nargs="+",
        default=list(DEFAULT_DATASETS),
        help="Processed dataset roots to sample MCQs from.",
    )
    parser.add_argument("--count", type=int, default=DEFAULT_COUNT)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--output-jsonl", type=Path, default=DEFAULT_OUTPUT_JSONL)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--taxonomy", type=Path, default=TAXONOMY_PATH)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--api-base-url", default=DEFAULT_API_BASE)
    parser.add_argument("--api-key", default=os.environ.get("OPENROUTER_API_KEY", ""))
    parser.add_argument(
        "--max-classify",
        type=int,
        default=None,
        help="Stop after this many API classifications (debug).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Reuse existing processed labels; do not call OpenRouter.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Append to existing output and skip duplicate questions.",
    )
    args = parser.parse_args()

    entries = load_taxonomy(args.taxonomy)
    candidates = collect_candidates(args.datasets)
    if not candidates:
        raise SystemExit("No MCQ candidates found in the configured dataset roots.")

    rng = random.Random(args.seed)
    rng.shuffle(candidates)

    raw_paths = sorted(
        {
            processed_to_raw_path(path)
            for _, path in candidates
            if processed_to_raw_path(path) is not None
        }
    )
    raw_index = build_raw_question_index([p for p in raw_paths if p is not None])

    existing_rows: list[dict[str, Any]] = []
    kept_questions: set[str] = set()
    if args.resume and args.output_jsonl.is_file():
        existing_rows = list(iter_jsonl(args.output_jsonl))
        kept_questions = load_existing_questions(args.output_jsonl)
        print(f"Resuming with {len(existing_rows)} existing gold rows.", file=sys.stderr)

    classifier: FrontierClassifier | None = None
    if not args.dry_run:
        if not args.api_key:
            raise SystemExit("Set OPENROUTER_API_KEY or pass --api-key (or use --dry-run).")
        classifier = FrontierClassifier(
            model=args.model,
            api_base_url=args.api_base_url,
            api_key=args.api_key,
            entries=entries,
        )

    selected = list(existing_rows)
    skipped_other = 0
    classified = 0
    next_id = len(selected) + 1

    for record, processed_file in candidates:
        if len(selected) >= args.count:
            break
        payload = record.get("payload") or {}
        question = normalize_question(str(payload.get("question") or ""))
        if question in kept_questions:
            continue

        norm_payload = normalize_payload(record)
        if args.dry_run:
            result = dry_run_classification(record)
        else:
            assert classifier is not None
            result = classifier.classify(
                norm_payload["question"],
                norm_payload["choices"],
            )
            classified += 1

        if result["predicted_label"] == OTHER_LABEL:
            skipped_other += 1
            continue

        gold_id = f"gold_{next_id:06d}"
        next_id += 1
        selected.append(
            build_gold_record(
                gold_id=gold_id,
                source=record,
                processed_file=processed_file,
                classification=result,
                model=args.model if not args.dry_run else "dry-run",
                raw_index=raw_index,
            )
        )
        kept_questions.add(question)
        print(
            f"[{len(selected)}/{args.count}] {gold_id} {result['predicted_label']} "
            f"({result['predicted_label_name']})",
            file=sys.stderr,
        )

        if (
            not args.dry_run
            and args.max_classify is not None
            and classified >= args.max_classify
        ):
            print(f"Reached --max-classify={args.max_classify}; stopping.", file=sys.stderr)
            break

    if len(selected) < args.count:
        print(
            f"Warning: only collected {len(selected)}/{args.count} non-Other MCQs "
            f"({skipped_other} candidates classified as Other).",
            file=sys.stderr,
        )

    write_jsonl(args.output_jsonl, selected)
    write_csv(args.output_csv, selected)
    print(f"Wrote {display_path(args.output_jsonl)} ({len(selected)} rows)")
    print(f"Wrote {display_path(args.output_csv)}")


if __name__ == "__main__":
    main()
