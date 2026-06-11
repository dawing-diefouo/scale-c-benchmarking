#!/usr/bin/env python3
"""Run cyber LLMs on Scale_C benchmark records and score against payload gold answers.

Results are written under data/eval/<corpus>/ (embedding or nli), matching the corpus
under data/final/<corpus>/ used as --input.
"""

from __future__ import annotations

import argparse
import csv
import gc
import json
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINAL_DATA_ROOT = ROOT / "data" / "final"
EVAL_DATA_ROOT = ROOT / "data" / "eval"
CORPUS_CHOICES = ("embedding", "nli")
DEFAULT_CORPUS = "embedding"
DEFAULT_MODELS_CONFIG = ROOT / "config" / "eval_models.json"


def corpus_input_dir(corpus: str) -> Path:
    if corpus not in CORPUS_CHOICES:
        raise ValueError(f"Unknown corpus {corpus!r}; expected one of {CORPUS_CHOICES}")
    return FINAL_DATA_ROOT / corpus


def corpus_output_dir(corpus: str) -> Path:
    return EVAL_DATA_ROOT / corpus


def infer_corpus_from_path(path: Path) -> str | None:
    resolved = path.resolve()
    for name in CORPUS_CHOICES:
        corpus_root = corpus_input_dir(name).resolve()
        if resolved == corpus_root or corpus_root in resolved.parents:
            return name
    return None


def resolve_eval_paths(
    *,
    corpus: str | None,
    input_path: Path | None,
    output_dir: Path | None,
) -> tuple[str, Path, Path]:
    if corpus is not None and corpus not in CORPUS_CHOICES:
        raise SystemExit(f"Unknown --corpus {corpus!r}; choose from: {', '.join(CORPUS_CHOICES)}")

    if input_path is not None:
        resolved_input = input_path.expanduser().resolve()
        inferred = infer_corpus_from_path(resolved_input)
        if corpus is not None and inferred is not None and inferred != corpus:
            raise SystemExit(
                f"--corpus {corpus!r} does not match --input {resolved_input} (looks like {inferred!r})."
            )
        active_corpus = corpus or inferred
        if active_corpus is None:
            raise SystemExit(
                "Could not infer corpus from --input. Pass --corpus embedding or --corpus nli, "
                "or use data/final/embedding or data/final/nli as input."
            )
        active_input = resolved_input
    elif corpus is not None:
        active_corpus = corpus
        active_input = corpus_input_dir(corpus)
    else:
        active_corpus = DEFAULT_CORPUS
        active_input = corpus_input_dir(DEFAULT_CORPUS)

    active_output = (
        output_dir.expanduser().resolve()
        if output_dir is not None
        else corpus_output_dir(active_corpus)
    )
    return active_corpus, active_input, active_output

LETTER_RE = re.compile(r"\b([A-Z])\b")
MULTI_LETTER_RE = re.compile(r"\b([A-Z])\b")


@dataclass(frozen=True)
class ModelSpec:
    alias: str
    display_name: str
    model_id: str
    backend: str
    notes: str = ""
    is_base: bool = False
    base_model_alias: str = ""


@dataclass(frozen=True)
class GoldAnswer:
    value: str | list[str]
    kind: str  # letter | multi_letter | text


@dataclass(frozen=True)
class PromptSpec:
    text: str
    option_letters: list[str]
    multi_select: bool


def load_model_registry(path: Path) -> dict[str, ModelSpec]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    registry: dict[str, ModelSpec] = {}
    for alias, entry in raw.items():
        registry[alias] = ModelSpec(
            alias=alias,
            display_name=entry["display_name"],
            model_id=entry["model_id"],
            backend=entry["backend"],
            notes=entry.get("notes", ""),
            is_base=entry.get("is_base", False),
            base_model_alias=entry.get("base_model_alias", ""),
        )
    return registry


def iter_jsonl_files(path: Path, *, include_by_topic: bool = False) -> list[Path]:
    if path.is_file():
        if path.suffix != ".jsonl":
            raise ValueError(f"Expected a .jsonl file, got: {path}")
        return [path]
    if not path.is_dir():
        raise FileNotFoundError(path)

    dataset_files = sorted(path.glob("*/dataset.jsonl"))
    if dataset_files and not include_by_topic:
        return dataset_files

    files = sorted(path.rglob("*.jsonl"))
    if not files:
        raise ValueError(f"No .jsonl files under {path}")
    return files


def iter_records(
    input_path: Path,
    *,
    limit: int | None = None,
    task_types: set[str] | None = None,
    include_by_topic: bool = False,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for jsonl_path in iter_jsonl_files(input_path, include_by_topic=include_by_topic):
        with jsonl_path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                if task_types and record.get("task_type") not in task_types:
                    continue
                records.append(record)
                if limit is not None and len(records) >= limit:
                    return records
    return records


def index_to_letter(index: int) -> str | None:
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if 0 <= index < len(letters):
        return letters[index]
    return None


def normalize_letter(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip().upper()
    match = LETTER_RE.search(text)
    return match.group(1) if match else None


def extract_option_letter(option_text: str, fallback_index: int) -> str:
    text = option_text.strip()
    match = re.match(r"^([A-Z])\s*[\).:-]", text, flags=re.IGNORECASE)
    if match:
        return match.group(1).upper()
    letter = index_to_letter(fallback_index)
    return letter or "?"


def get_mcq_options(payload: dict[str, Any]) -> list[tuple[str, str]]:
    if isinstance(payload.get("choices"), dict):
        return [(key.upper(), str(value)) for key, value in payload["choices"].items()]
    if isinstance(payload.get("answers"), dict) and "question" in payload:
        return [(key.upper(), str(value)) for key, value in payload["answers"].items()]
    if isinstance(payload.get("choices"), list):
        return [
            (extract_option_letter(text, idx), text)
            for idx, text in enumerate(payload["choices"])
        ]
    if isinstance(payload.get("options"), list):
        return [
            (extract_option_letter(text, idx), text)
            for idx, text in enumerate(payload["options"])
        ]
    option_pairs: list[tuple[str, str]] = []
    for idx, key in enumerate(("option_a", "option_b", "option_c", "option_d", "option_e")):
        if payload.get(key):
            letter = index_to_letter(idx)
            if letter:
                option_pairs.append((letter, str(payload[key])))
    return option_pairs


def extract_gold_answer(record: dict[str, Any]) -> GoldAnswer | None:
    payload = record.get("payload") or {}
    evaluation = record.get("evaluation") or {}

    correct = evaluation.get("correct_answer")
    if isinstance(correct, str):
        letter = normalize_letter(correct)
        if letter:
            return GoldAnswer(letter, "letter")
        if correct.strip():
            return GoldAnswer(correct.strip(), "text")
    if isinstance(correct, list):
        letters = sorted({letter for letter in (normalize_letter(item) for item in correct) if letter})
        if letters:
            return GoldAnswer(letters, "multi_letter")

    solution = payload.get("solution")
    if isinstance(solution, str) and solution.strip():
        letter = normalize_letter(solution)
        if letter:
            return GoldAnswer(letter, "letter")

    if isinstance(payload.get("answer"), int):
        letter = index_to_letter(payload["answer"])
        if letter:
            return GoldAnswer(letter, "letter")

    answers = payload.get("answers")
    if isinstance(answers, list) and answers:
        letters = sorted({letter for letter in (normalize_letter(item) for item in answers) if letter})
        if letters:
            return GoldAnswer(letters, "multi_letter")

    if isinstance(payload.get("output"), str) and payload["output"].strip():
        return GoldAnswer(payload["output"].strip(), "text")

    return None


def is_mcq_scorable(record: dict[str, Any], gold: GoldAnswer | None) -> bool:
    if gold is None:
        return False
    if gold.kind in {"letter", "multi_letter"}:
        return bool(get_mcq_options(record.get("payload") or {}))
    return False


def build_prompt(record: dict[str, Any], gold: GoldAnswer) -> PromptSpec | None:
    payload = record.get("payload") or {}
    options = get_mcq_options(payload)
    if not options:
        return None

    question = (
        payload.get("question")
        or payload.get("prompt")
        or payload.get("instruction")
        or ""
    ).strip()
    if not question:
        return None

    option_letters = [letter for letter, _ in options]
    multi_select = gold.kind == "multi_letter"
    options_text = "\n".join(f"{letter}) {text}" for letter, text in options)

    if multi_select:
        instruction = (
            "Answer this cybersecurity multiple-choice question. "
            f"Select all correct options from {', '.join(option_letters)}. "
            "Reply with only the letters separated by commas (e.g. A, C)."
        )
    else:
        instruction = (
            "Answer this cybersecurity multiple-choice question with only one letter "
            f"from {', '.join(option_letters)}."
        )

    prompt = f"""{instruction}

Question:
{question}

Options:
{options_text}

Answer:"""

    return PromptSpec(text=prompt, option_letters=option_letters, multi_select=multi_select)


def parse_single_letter(response: str, allowed: list[str]) -> str | None:
    text = response.strip().upper()
    allowed_set = set(allowed)

    patterns = (
        r"ANSWER\s*(?:IS\s*)?[:\-]?\s*([A-Z])\b",
        r"OPTION\s*(?:IS\s*)?[:\-]?\s*([A-Z])\b",
        r"CHOICE\s*(?:IS\s*)?[:\-]?\s*([A-Z])\b",
        r"\(([A-Z])\)",
    )
    for pattern in patterns:
        match = re.search(pattern, text)
        if match and match.group(1) in allowed_set:
            return match.group(1)

    letters = [letter for letter in MULTI_LETTER_RE.findall(text) if letter in allowed_set]
    if letters:
        return letters[-1]

    return None


def parse_multi_letter(response: str, allowed: list[str]) -> list[str] | None:
    allowed_set = set(allowed)
    letters = [letter for letter in MULTI_LETTER_RE.findall(response.upper()) if letter in allowed_set]
    if not letters:
        return None
    return sorted(set(letters))


def score_prediction(gold: GoldAnswer, parsed: Any) -> tuple[float, bool]:
    if parsed is None:
        return 0.0, False
    if gold.kind == "letter":
        return (1.0, True) if parsed == gold.value else (0.0, False)
    if gold.kind == "multi_letter":
        return (1.0, True) if parsed == gold.value else (0.0, False)
    if gold.kind == "text" and isinstance(parsed, str):
        normalized_gold = " ".join(str(gold.value).split()).lower()
        normalized_pred = " ".join(parsed.split()).lower()
        return (1.0, True) if normalized_gold == normalized_pred else (0.0, False)
    return 0.0, False


def configure_hf_cache(cache_dir: Path | None) -> Path:
    if cache_dir is None:
        return Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface")).expanduser()

    cache_dir = cache_dir.expanduser().resolve()
    cache_dir.mkdir(parents=True, exist_ok=True)
    hub_cache = cache_dir / "hub"
    hub_cache.mkdir(parents=True, exist_ok=True)
    os.environ["HF_HOME"] = str(cache_dir)
    os.environ["HUGGINGFACE_HUB_CACHE"] = str(hub_cache)
    os.environ["TRANSFORMERS_CACHE"] = str(hub_cache)
    return cache_dir


def dir_size_bytes(path: Path) -> int:
    total = 0
    if not path.exists():
        return 0
    for entry in path.rglob("*"):
        if entry.is_file():
            total += entry.stat().st_size
    return total


def format_bytes(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


def largest_hf_model_caches(hub_cache: Path, *, limit: int = 8) -> list[tuple[str, int]]:
    models_root = hub_cache / "hub" if (hub_cache / "hub").is_dir() else hub_cache
    if not models_root.is_dir():
        return []
    sizes = [
        (path.name.removeprefix("models--").replace("--", "/"), dir_size_bytes(path))
        for path in models_root.glob("models--*")
    ]
    sizes.sort(key=lambda item: item[1], reverse=True)
    return sizes[:limit]


def cleanup_incomplete_hf_downloads(hub_cache: Path) -> tuple[int, int]:
    models_root = hub_cache / "hub" if (hub_cache / "hub").is_dir() else hub_cache
    if not models_root.is_dir():
        return 0, 0

    removed_files = 0
    reclaimed = 0
    for incomplete in models_root.rglob("*.incomplete"):
        reclaimed += incomplete.stat().st_size
        incomplete.unlink(missing_ok=True)
        removed_files += 1

    locks_root = models_root / ".locks"
    if locks_root.is_dir():
        for lock_file in locks_root.rglob("*.lock"):
            lock_file.unlink(missing_ok=True)
            removed_files += 1
    return removed_files, reclaimed


def raise_disk_quota_help(exc: BaseException, *, hub_cache: Path, model_id: str) -> None:
    removed, reclaimed = cleanup_incomplete_hf_downloads(hub_cache)
    largest = largest_hf_model_caches(hub_cache)
    lines = [
        f"Model download/load failed for {model_id!r}: {exc}",
        "",
        "Likely cause: home disk quota exceeded while writing to the Hugging Face cache.",
        f"Cache directory: {hub_cache}",
    ]
    if removed:
        lines.append(
            f"Auto-removed {removed} incomplete download artifact(s), "
            f"reclaiming about {format_bytes(reclaimed)}."
        )
    if largest:
        lines.append("")
        lines.append("Largest cached models:")
        for name, size in largest:
            lines.append(f"  - {name}: {format_bytes(size)}")
    lines.extend(
        [
            "",
            "Free ~15GB for a 7B model, then retry. Options:",
            "  huggingface-cli delete-cache",
            "  python3 scripts/eval_llm_benchmark.py --cleanup-incomplete-downloads",
            "  python3 scripts/eval_llm_benchmark.py --hf-cache-dir /path/with/space/hf ...",
        ]
    )
    raise SystemExit("\n".join(lines)) from exc


def pick_device(choice: str) -> str:
    import torch

    if choice != "auto":
        return choice
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


class HuggingFaceGenerator:
    def __init__(
        self,
        model_id: str,
        *,
        device: str,
        max_new_tokens: int,
        trust_remote_code: bool = True,
        hub_cache: Path | None = None,
        local_files_only: bool = False,
    ) -> None:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        print(f"Loading {model_id} on {device}...", file=sys.stderr)
        self.model_id = model_id
        load_kwargs: dict[str, Any] = {
            "trust_remote_code": trust_remote_code,
            "local_files_only": local_files_only,
        }
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_id, **load_kwargs)
            dtype = torch.bfloat16 if device in {"cuda", "mps"} else torch.float32
            model_kwargs = {**load_kwargs, "dtype": dtype}
            if device == "cuda":
                model_kwargs["device_map"] = "auto"
            self.model = AutoModelForCausalLM.from_pretrained(model_id, **model_kwargs)
        except OSError as exc:
            if getattr(exc, "errno", None) == 122 or "Disk quota exceeded" in str(exc):
                cache_root = hub_cache or configure_hf_cache(None)
                raise_disk_quota_help(exc, hub_cache=cache_root, model_id=str(model_id))
            raise
        if device != "cuda":
            self.model = self.model.to(device)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.device = device if device != "cuda" else next(self.model.parameters()).device.type
        self.max_new_tokens = max_new_tokens
        self.model.eval()

    def generate(self, prompt: str) -> str:
        import torch

        messages = [{"role": "user", "content": prompt}]
        if getattr(self.tokenizer, "chat_template", None):
            formatted = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        else:
            formatted = prompt

        inputs = self.tokenizer(
            formatted,
            return_tensors="pt",
            truncation=True,
            max_length=4096,
        )
        target_device = next(self.model.parameters()).device
        inputs = {key: value.to(target_device) for key, value in inputs.items()}
        input_length = inputs["input_ids"].shape[1]

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        generated = outputs[0][input_length:]
        return self.tokenizer.decode(generated, skip_special_tokens=True).strip()

    def unload(self) -> None:
        import torch

        del self.model
        del self.tokenizer
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


class OpenAICompatibleGenerator:
    def __init__(
        self,
        model_id: str,
        *,
        api_base_url: str,
        api_key: str,
        max_new_tokens: int,
    ) -> None:
        self.model_id = model_id
        self.api_base_url = api_base_url.rstrip("/")
        self.api_key = api_key
        self.max_new_tokens = max_new_tokens

    def generate(self, prompt: str) -> str:
        import urllib.error
        import urllib.request

        payload = {
            "model": self.model_id,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self.max_new_tokens,
            "temperature": 0,
        }
        request = urllib.request.Request(
            f"{self.api_base_url}/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"API request failed ({exc.code}): {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"API unreachable at {self.api_base_url}: {exc.reason}") from exc
        return body["choices"][0]["message"]["content"].strip()


def verify_openai_api(api_base_url: str, api_key: str, model_id: str) -> None:
    import urllib.error
    import urllib.request

    base = api_base_url.rstrip("/")
    request = urllib.request.Request(
        f"{base}/v1/models",
        headers={"Authorization": f"Bearer {api_key}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status != 200:
                raise RuntimeError(f"Unexpected status {response.status}")
    except urllib.error.URLError as exc:
        raise SystemExit(
            "\n".join(
                [
                    f"Cannot reach OpenAI-compatible API at {base}.",
                    f"Reason: {exc.reason}",
                    "",
                    "Nothing is serving that URL, so models like BaronLLM/Trendyol 70B cannot run this way.",
                    "In a limited environment without Ollama/vLLM, use HuggingFace-backed models instead:",
                    "  python3 scripts/eval_llm_benchmark.py --model lily-cyber-7b",
                    "  python3 scripts/eval_llm_benchmark.py --model foundation-sec-8b",
                    "  python3 scripts/eval_llm_benchmark.py --model zysec-7b",
                ]
            )
        ) from exc
    print(f"API reachable at {base} (model id sent as {model_id!r}).", file=sys.stderr)


class ChoiceRankingGenerator:
    """Rank MCQ options with an encoder by cosine similarity (CyBERTuned)."""

    def __init__(self, model_id: str, *, device: str) -> None:
        import torch
        from transformers import AutoModel, AutoTokenizer

        print(f"Loading encoder {model_id} on {device}...", file=sys.stderr)
        self.model_id = model_id
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModel.from_pretrained(model_id).to(device)
        self.model.eval()
        self.device = device

    def _encode(self, text: str):
        import torch

        encoded = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )
        encoded = {key: value.to(self.device) for key, value in encoded.items()}
        with torch.no_grad():
            hidden = self.model(**encoded).last_hidden_state
        lengths = encoded["attention_mask"].sum(dim=-1)
        return hidden[0, : lengths[0]].mean(dim=0)

    def rank_options(self, question: str, options: list[tuple[str, str]]) -> str:
        import torch

        question_vec = self._encode(question)
        best_letter = options[0][0]
        best_score = float("-inf")
        for letter, text in options:
            option_vec = self._encode(text)
            score = torch.nn.functional.cosine_similarity(
                question_vec.unsqueeze(0),
                option_vec.unsqueeze(0),
            ).item()
            if score > best_score:
                best_score = score
                best_letter = letter
        return best_letter

    def generate(self, prompt: str) -> str:
        raise NotImplementedError("Use rank_options for choice_ranking backend")

    def unload(self) -> None:
        import torch

        del self.model
        del self.tokenizer
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


def build_generator(
    spec: ModelSpec,
    *,
    device: str,
    max_new_tokens: int,
    api_base_url: str | None,
    api_key: str,
    hub_cache: Path,
    model_paths: dict[str, Path],
    local_files_only: bool,
) -> HuggingFaceGenerator | OpenAICompatibleGenerator | ChoiceRankingGenerator:
    if spec.backend == "huggingface":
        model_source = str(model_paths.get(spec.alias, spec.model_id))
        return HuggingFaceGenerator(
            model_source,
            device=device,
            max_new_tokens=max_new_tokens,
            hub_cache=hub_cache,
            local_files_only=local_files_only,
        )
    if spec.backend == "openai":
        if not api_base_url:
            raise SystemExit(
                f"Model {spec.alias!r} ({spec.display_name}) requires an OpenAI-compatible server.\n"
                f"Serve {spec.model_id} with vLLM or Ollama, then pass --api-base-url.\n"
                "Without a local server, use a HuggingFace-backed model instead "
                "(lily-cyber-7b, foundation-sec-8b, zysec-7b, cybertuned)."
            )
        verify_openai_api(api_base_url, api_key, spec.model_id)
        return OpenAICompatibleGenerator(
            spec.model_id,
            api_base_url=api_base_url,
            api_key=api_key,
            max_new_tokens=max_new_tokens,
        )
    if spec.backend == "choice_ranking":
        return ChoiceRankingGenerator(spec.model_id, device=device)
    raise SystemExit(f"Unsupported backend {spec.backend!r} for model {spec.alias!r}")


def load_completed_ids(output_path: Path) -> set[str]:
    if not output_path.exists():
        return set()
    completed: set[str] = set()
    with output_path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            record_id = record.get("id")
            if record_id:
                completed.add(record_id)
    return completed


def evaluate_record(
    record: dict[str, Any],
    *,
    spec: ModelSpec,
    corpus: str,
    generator: HuggingFaceGenerator | OpenAICompatibleGenerator | ChoiceRankingGenerator,
) -> dict[str, Any]:
    gold = extract_gold_answer(record)
    base = dict(record)
    evaluation_block: dict[str, Any] = {
        "corpus": corpus,
        "model_alias": spec.alias,
        "model": spec.model_id,
        "display_name": spec.display_name,
        "backend": spec.backend,
        "scorable": False,
        "skipped_reason": None,
        "raw_response": None,
        "parsed_answer": None,
        "correct_answer": gold.value if gold else None,
        "score": None,
        "is_correct": None,
    }

    if gold is None:
        evaluation_block["skipped_reason"] = "no_gold_answer"
        base["model_evaluation"] = evaluation_block
        return base

    if not is_mcq_scorable(record, gold):
        evaluation_block["skipped_reason"] = "unsupported_task_or_answer_format"
        base["model_evaluation"] = evaluation_block
        return base

    prompt_spec = build_prompt(record, gold)
    if prompt_spec is None:
        evaluation_block["skipped_reason"] = "prompt_build_failed"
        base["model_evaluation"] = evaluation_block
        return base

    evaluation_block["scorable"] = True
    try:
        if spec.backend == "choice_ranking":
            payload = record["payload"]
            question = (payload.get("question") or payload.get("prompt") or "").strip()
            options = get_mcq_options(payload)
            raw = generator.rank_options(question, options)  # type: ignore[attr-defined]
            parsed: Any = raw
        else:
            raw = generator.generate(prompt_spec.text)  # type: ignore[attr-defined]
            parsed = (
                parse_multi_letter(raw, prompt_spec.option_letters)
                if prompt_spec.multi_select
                else parse_single_letter(raw, prompt_spec.option_letters)
            )
        score, is_correct = score_prediction(gold, parsed)
        evaluation_block.update(
            {
                "raw_response": raw,
                "parsed_answer": parsed,
                "score": score,
                "is_correct": is_correct,
            }
        )
    except Exception as exc:  # noqa: BLE001 - keep eval loop running
        evaluation_block["scorable"] = False
        evaluation_block["skipped_reason"] = f"inference_error: {exc}"

    base["model_evaluation"] = evaluation_block
    return base


def summarize_results(
    output_path: Path,
    spec: ModelSpec,
    *,
    corpus: str,
    input_dir: Path,
) -> dict[str, Any]:
    totals = Counter()
    correct = Counter()
    by_task = defaultdict(lambda: {"total": 0, "correct": 0})
    by_source = defaultdict(lambda: {"total": 0, "correct": 0})
    by_topic = defaultdict(lambda: {"total": 0, "correct": 0})
    by_difficulty = defaultdict(lambda: {"total": 0, "correct": 0})
    by_risk = defaultdict(lambda: {"total": 0, "correct": 0})
    by_cognitive = defaultdict(lambda: {"total": 0, "correct": 0})
    by_tier = defaultdict(lambda: {"total": 0, "correct": 0})

    with output_path.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            me = record.get("model_evaluation") or {}
            if not me.get("scorable"):
                reason = me.get("skipped_reason") or ""
                if reason.startswith("inference_error"):
                    totals["errors"] += 1
                else:
                    totals["skipped"] += 1
                continue
            totals["scorable"] += 1
            metadata = record.get("metadata") or {}
            task = record.get("task_type", "unknown")
            source = metadata.get("source", "unknown")
            topic = ((record.get("classification") or {}).get("predicted_label")) or "unknown"
            difficulty = metadata.get("difficulty") or metadata.get("difficulty.json") or "unknown"
            risk = metadata.get("risk_category") or "unknown"
            cognitive = metadata.get("cognitive_skill") or "unknown"
            tier = f"tier{record.get('tier', 'unknown')}"
            by_task[task]["total"] += 1
            by_source[source]["total"] += 1
            by_topic[topic]["total"] += 1
            by_difficulty[difficulty]["total"] += 1
            by_risk[risk]["total"] += 1
            by_cognitive[cognitive]["total"] += 1
            by_tier[tier]["total"] += 1
            if me.get("is_correct"):
                totals["correct"] += 1
                by_task[task]["correct"] += 1
                by_source[source]["correct"] += 1
                by_topic[topic]["correct"] += 1
                by_difficulty[difficulty]["correct"] += 1
                by_risk[risk]["correct"] += 1
                by_cognitive[cognitive]["correct"] += 1
                by_tier[tier]["correct"] += 1

    accuracy = (totals["correct"] / totals["scorable"]) if totals["scorable"] else 0.0
    return {
        "corpus": corpus,
        "input_dir": str(input_dir),
        "model_alias": spec.alias,
        "model": spec.model_id,
        "display_name": spec.display_name,
        "backend": spec.backend,
        "is_base": spec.is_base,
        "base_model_alias": spec.base_model_alias or None,
        "totals": dict(totals),
        "accuracy": accuracy,
        "by_task_type": dict(by_task),
        "by_source": dict(by_source),
        "by_topic": dict(by_topic),
        "by_difficulty": dict(by_difficulty),
        "by_risk_category": dict(by_risk),
        "by_cognitive_skill": dict(by_cognitive),
        "by_tier": dict(by_tier),
        "output_file": str(output_path),
    }


def run_model_eval(
    records: list[dict[str, Any]],
    *,
    spec: ModelSpec,
    corpus: str,
    input_dir: Path,
    output_dir: Path,
    device: str,
    max_new_tokens: int,
    resume: bool,
    api_base_url: str | None,
    api_key: str,
    hub_cache: Path,
    model_paths: dict[str, Path],
    local_files_only: bool,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{spec.alias}.jsonl"
    summary_path = output_dir / f"{spec.alias}_summary.json"
    completed = load_completed_ids(output_path) if resume else set()
    mode = "a" if resume and output_path.exists() else "w"

    generator = build_generator(
        spec,
        device=device,
        max_new_tokens=max_new_tokens,
        api_base_url=api_base_url,
        api_key=api_key,
        hub_cache=hub_cache,
        model_paths=model_paths,
        local_files_only=local_files_only,
    )

    processed = 0
    with output_path.open(mode, encoding="utf-8") as handle:
        for record in records:
            record_id = record.get("id")
            if record_id and record_id in completed:
                continue
            result = evaluate_record(record, spec=spec, corpus=corpus, generator=generator)
            handle.write(json.dumps(result, ensure_ascii=False) + "\n")
            processed += 1
            if processed % 25 == 0:
                print(f"  {spec.alias}: wrote {processed} new rows...", file=sys.stderr)

    if hasattr(generator, "unload"):
        generator.unload()

    summary = summarize_results(output_path, spec, corpus=corpus, input_dir=input_dir)
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"{spec.display_name}: accuracy={summary['accuracy']:.1%} "
        f"({summary['totals'].get('correct', 0)}/{summary['totals'].get('scorable', 0)} scorable)",
        file=sys.stderr,
    )
    return summary


def write_comparison(summary_paths: list[Path], output_dir: Path) -> Path:
    rows = []
    for path in summary_paths:
        rows.append(json.loads(path.read_text(encoding="utf-8")))
    rows.sort(key=lambda item: item.get("accuracy", 0.0), reverse=True)
    comparison_path = output_dir / "comparison.json"
    comparison_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return comparison_path


def group_accuracy(group: dict[str, Any]) -> float | None:
    total = group.get("total", 0)
    if not total:
        return None
    return group.get("correct", 0) / total


def write_base_model_comparisons(output_dir: Path) -> tuple[Path | None, Path | None]:
    summaries = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(output_dir.glob("*_summary.json"))
    ]
    by_alias = {summary["model_alias"]: summary for summary in summaries}
    overall_rows: list[dict[str, Any]] = []
    category_rows: list[dict[str, Any]] = []
    category_fields = {
        "task_type": "by_task_type",
        "difficulty": "by_difficulty",
        "risk_category": "by_risk_category",
        "cognitive_skill": "by_cognitive_skill",
        "tier": "by_tier",
        "topic": "by_topic",
        "source": "by_source",
    }

    for ft in summaries:
        base_alias = ft.get("base_model_alias")
        if not base_alias or ft.get("is_base"):
            continue
        base = by_alias.get(base_alias)
        if not base:
            continue

        ft_acc = ft.get("accuracy", 0.0)
        base_acc = base.get("accuracy", 0.0)
        overall_rows.append(
            {
                "corpus": ft.get("corpus"),
                "ft_model": ft.get("model_alias"),
                "base_model": base_alias,
                "ft_accuracy": ft_acc,
                "base_accuracy": base_acc,
                "margin_pp": (ft_acc - base_acc) * 100,
                "ft_correct": ft.get("totals", {}).get("correct", 0),
                "ft_scorable": ft.get("totals", {}).get("scorable", 0),
                "base_correct": base.get("totals", {}).get("correct", 0),
                "base_scorable": base.get("totals", {}).get("scorable", 0),
            }
        )

        for category_name, summary_key in category_fields.items():
            ft_groups = ft.get(summary_key, {})
            base_groups = base.get(summary_key, {})
            for value in sorted(set(ft_groups) | set(base_groups)):
                ft_group = ft_groups.get(value, {"total": 0, "correct": 0})
                base_group = base_groups.get(value, {"total": 0, "correct": 0})
                ft_group_acc = group_accuracy(ft_group)
                base_group_acc = group_accuracy(base_group)
                category_rows.append(
                    {
                        "corpus": ft.get("corpus"),
                        "category": category_name,
                        "value": value,
                        "ft_model": ft.get("model_alias"),
                        "base_model": base_alias,
                        "ft_accuracy": ft_group_acc,
                        "base_accuracy": base_group_acc,
                        "margin_pp": (
                            (ft_group_acc - base_group_acc) * 100
                            if ft_group_acc is not None and base_group_acc is not None
                            else None
                        ),
                        "ft_correct": ft_group.get("correct", 0),
                        "ft_total": ft_group.get("total", 0),
                        "base_correct": base_group.get("correct", 0),
                        "base_total": base_group.get("total", 0),
                    }
                )

    if not overall_rows:
        return None, None

    overall_path = output_dir / "base_vs_finetuned_margins.csv"
    category_path = output_dir / "base_vs_finetuned_by_category.csv"
    with overall_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(overall_rows[0]))
        writer.writeheader()
        writer.writerows(overall_rows)
    with category_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(category_rows[0]))
        writer.writeheader()
        writer.writerows(category_rows)
    return overall_path, category_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate cyber LLMs on Scale_C records from data/final/embedding or data/final/nli.",
    )
    parser.add_argument(
        "--corpus",
        choices=CORPUS_CHOICES,
        default=None,
        help=(
            "Corpus variant under data/final/ (embedding or nli). "
            "Inferred from --input when omitted; default input/output corpus is embedding."
        ),
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="JSONL file or directory (default: data/final/<corpus>).",
    )
    parser.add_argument(
        "--models-config",
        type=Path,
        default=DEFAULT_MODELS_CONFIG,
        help="JSON registry of model aliases (default: config/eval_models.json).",
    )
    parser.add_argument(
        "--model",
        action="append",
        dest="models",
        help="Model alias from config (repeatable). Default: all HuggingFace models.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for per-model JSONL results (default: data/eval/<corpus>/).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Evaluate at most N records (after filters).",
    )
    parser.add_argument(
        "--task-types",
        nargs="+",
        default=None,
        help="Only evaluate these task_type values (e.g. mcq_answering open_explanation).",
    )
    parser.add_argument(
        "--device",
        choices=("auto", "cpu", "cuda", "mps"),
        default="auto",
        help="Device for HuggingFace / encoder backends.",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=32,
        help="Generation cap for model responses.",
    )
    parser.add_argument(
        "--api-base-url",
        default=None,
        help="OpenAI-compatible base URL for GGUF-served models (vLLM/Ollama).",
    )
    parser.add_argument(
        "--api-key",
        default="local",
        help="Bearer token for --api-base-url (default: local).",
    )
    parser.add_argument(
        "--hf-cache-dir",
        type=Path,
        default=None,
        help="Hugging Face cache root (sets HF_HOME). Default: ~/.cache/huggingface",
    )
    parser.add_argument(
        "--local-model-path",
        action="append",
        default=[],
        metavar="ALIAS=PATH",
        help="Load a model alias from a local directory instead of downloading.",
    )
    parser.add_argument(
        "--local-files-only",
        action="store_true",
        help="Do not download from Hugging Face; require models to already be cached locally.",
    )
    parser.add_argument(
        "--cleanup-incomplete-downloads",
        action="store_true",
        help="Remove stale *.incomplete files from the HF cache and exit.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip record ids already present in the output JSONL.",
    )
    parser.add_argument(
        "--include-by-topic",
        action="store_true",
        help="Also evaluate by_topic/*.jsonl shards (duplicates dataset.jsonl rows).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print dataset stats and exit without loading models.",
    )
    return parser.parse_args()


def parse_model_paths(values: list[str]) -> dict[str, Path]:
    mapping: dict[str, Path] = {}
    for item in values:
        if "=" not in item:
            raise SystemExit(f"Invalid --local-model-path {item!r}; expected ALIAS=PATH")
        alias, raw_path = item.split("=", 1)
        path = Path(raw_path).expanduser().resolve()
        if not path.is_dir():
            raise SystemExit(f"Local model path for {alias!r} not found: {path}")
        mapping[alias.strip()] = path
    return mapping


def main() -> None:
    args = parse_args()
    if args.device == "cpu":
        os.environ["CUDA_VISIBLE_DEVICES"] = ""

    hub_cache = configure_hf_cache(args.hf_cache_dir)
    if args.cleanup_incomplete_downloads:
        removed, reclaimed = cleanup_incomplete_hf_downloads(hub_cache)
        print(
            f"Removed {removed} incomplete download artifact(s) from {hub_cache}, "
            f"reclaimed about {format_bytes(reclaimed)}.",
            file=sys.stderr,
        )
        return

    model_paths = parse_model_paths(args.local_model_path)
    corpus, input_dir, output_dir = resolve_eval_paths(
        corpus=args.corpus,
        input_path=args.input,
        output_dir=args.output_dir,
    )
    registry = load_model_registry(args.models_config)
    if args.models:
        selected = []
        for alias in args.models:
            if alias not in registry:
                known = ", ".join(sorted(registry))
                raise SystemExit(f"Unknown model alias {alias!r}. Known: {known}")
            selected.append(registry[alias])
    else:
        selected = [
            spec
            for spec in registry.values()
            if spec.backend == "huggingface" and not spec.is_base
        ]

    task_types = set(args.task_types) if args.task_types else None
    records = iter_records(
        input_dir,
        limit=args.limit,
        task_types=task_types,
        include_by_topic=args.include_by_topic,
    )
    if not records:
        raise SystemExit(f"No records found under {input_dir}")

    scorable = sum(1 for record in records if is_mcq_scorable(record, extract_gold_answer(record)))
    print(
        f"Corpus: {corpus} | input: {input_dir} | output: {output_dir}",
        file=sys.stderr,
    )
    print(
        f"Loaded {len(records)} records; {scorable} MCQ-scorable with gold answers.",
        file=sys.stderr,
    )

    if args.dry_run:
        task_counts = Counter(record.get("task_type", "unknown") for record in records)
        print(
            json.dumps(
                {
                    "corpus": corpus,
                    "input_dir": str(input_dir),
                    "output_dir": str(output_dir),
                    "records": len(records),
                    "mcq_scorable": scorable,
                    "task_types": dict(task_counts),
                },
                indent=2,
            )
        )
        return

    device = pick_device(args.device)
    summaries: list[Path] = []
    for spec in selected:
        print(f"\n=== Evaluating {spec.display_name} ({spec.model_id}) ===", file=sys.stderr)
        summary = run_model_eval(
            records,
            spec=spec,
            corpus=corpus,
            input_dir=input_dir,
            output_dir=output_dir,
            device=device,
            max_new_tokens=args.max_new_tokens,
            resume=args.resume,
            api_base_url=args.api_base_url,
            api_key=args.api_key,
            hub_cache=hub_cache,
            model_paths=model_paths,
            local_files_only=args.local_files_only,
        )
        summaries.append(output_dir / f"{spec.alias}_summary.json")

    if len(summaries) > 1:
        comparison_path = write_comparison(summaries, output_dir)
        print(f"\nWrote comparison: {comparison_path}", file=sys.stderr)
    overall_comparison_path, category_comparison_path = write_base_model_comparisons(output_dir)
    if overall_comparison_path and category_comparison_path:
        print(f"Wrote base comparison: {overall_comparison_path}", file=sys.stderr)
        print(f"Wrote category comparison: {category_comparison_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
