"""Zero-shot topic classification for Scale_C benchmark rows.

Reads label names from ``schema/taxonomy.json``, classifies text derived from any
JSONL row shape, and writes Scale_C records (see ``schema/schema.json``) to
``data/processed/``. Edit the ``DEFAULT_*`` run configuration block at the top of
this file, then run with no CLI arguments; flags still override those defaults.

Supported backends (``--method``):

* ``nli`` — Hugging Face ``zero-shot-classification`` pipeline (MNLI / XNLI models).
* ``embedding`` — cosine similarity between text and label embeddings
  (``microsoft/LLM2CLIP-Llama-3-8B-Instruct-CC-Finetuned`` via mean-pooled
  Llama encoder, or any Sentence-Transformer model).
* ``generative`` — prompt a causal LM to pick one taxonomy label
  (``sknow-lab/Qwen2.5-14B-CIC-ACLARC``; GGUF ids are mapped to the transformers
  checkpoint automatically).
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Protocol

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema" / "taxonomy.json"
TAXONOMY_ROOT = ROOT / "schema" / "taxonomies"
PROCESSED = ROOT / "data" / "processed"
RAW_ROOT = ROOT / "data" / "raw"

# --- Run configuration (edit these, then: python scripts/classify_zero_shot.py) ---
DEFAULT_INPUT = ROOT / "data" / "raw" / "huggingface" / "mmlu" / "computer_security" / "test.jsonl"
DEFAULT_TAXONOMY = SCHEMA
DEFAULT_TAXONOMY_DIR = TAXONOMY_ROOT
DEFAULT_OUTPUT = PROCESSED / "cyberbech.jsonl"
DEFAULT_OUTPUT_ROOT = "qwen"
DEFAULT_METHOD = "generative"
DEFAULT_MODEL = "sknow-lab/Qwen2.5-14B-CIC-ACLARC"
DEFAULT_MULTI_LABEL = False
DEFAULT_TRUNCATE = False
DEFAULT_MAX_ROWS: int | None = None
DEFAULT_START = 0
DEFAULT_ID_PREFIX = "scale_c"
DEFAULT_GPU: int | None = None
DEFAULT_EXTRA_TAXONOMIES = ("tasks", "risks", "difficulty", "cognitive", "tiers")

METHOD_DEFAULT_MODELS = {
    "nli": "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7",
    "embedding": "microsoft/LLM2CLIP-Llama-3-8B-Instruct-CC-Finetuned",
    "generative": "sknow-lab/Qwen2.5-14B-CIC-ACLARC",
}

BENCHMARK = "scale_c"
SCHEMA_VERSION = 2
DEFAULT_TIER = 1
PLACEHOLDER = "-"

TEXT_KEYS = (
    "question",
    "text",
    "prompt",
    "instruction",
    "context",
    "sentence_1",
    "sentence_2",
    "premise",
    "hypothesis",
    "json_schema",
    "code",
    "passage",
    "article",
    "title",
    "claim",
    "statement",
)


@dataclass(frozen=True)
class TaxonomyEntry:
    id: str
    name: str
    candidate: str


class ClassifierBackend(Protocol):
    method: str
    model_id: str

    def classify(
        self,
        text: str,
        entries: list[TaxonomyEntry],
        *,
        multi_label: bool,
    ) -> tuple[list[str], list[float]]: ...


def pick_device(requested: str) -> int | str:
    """Map CLI device choice to Transformers pipeline ``device`` (-1 = CPU)."""
    import torch

    if requested == "cpu":
        return -1
    if requested == "cuda":
        if not torch.cuda.is_available():
            raise SystemExit(
                "CUDA was requested (--device cuda) but is not available. "
                "Update the NVIDIA driver, install a matching PyTorch build, or use --device cpu."
            )
        return 0
    if requested == "mps":
        mps = getattr(torch.backends, "mps", None)
        if mps is None or not mps.is_available():
            raise SystemExit("--device mps was requested but Apple MPS is not available.")
        return "mps"
    if torch.cuda.is_available():
        return 0
    mps = getattr(torch.backends, "mps", None)
    if mps is not None and mps.is_available():
        return "mps"
    return -1


def torch_device(device: int | str) -> str:
    if device == -1:
        return "cpu"
    if device == "mps":
        return "mps"
    return "cuda"


def resolve_model_id(model: str, method: str) -> str:
    if "gguf" not in model.casefold():
        return model
    if method != "generative":
        raise SystemExit(
            f"Model {model!r} is a GGUF checkpoint and is not supported by --method {method!r}. "
            "Use --method generative (maps to the transformers checkpoint) or run GGUF via llama.cpp."
        )
    resolved = re.sub(r"-gguf$", "", model, flags=re.I)
    if resolved != model:
        print(
            f"Note: GGUF weights are not loaded here; using transformers checkpoint {resolved!r}.",
            file=sys.stderr,
        )
    return resolved


def infer_method(model: str) -> str | None:
    folded = model.casefold()
    if "llm2clip" in folded:
        return "embedding"
    if "cic-aclarc" in folded or ("qwen" in folded and "cic" in folded):
        return "generative"
    if folded.endswith("-gguf"):
        return "generative"
    return None


def load_taxonomy(path: Path) -> list[TaxonomyEntry]:
    data = json.loads(path.read_text(encoding="utf-8"))
    entries: list[TaxonomyEntry] = []
    seen_candidates: set[str] = set()
    for raw in data["labels"]:
        name = str(raw["name"])
        label_id = str(raw.get("id", name))
        description = str(raw.get("description", "")).strip()
        candidate = f"{name}: {description}" if description else name
        if candidate in seen_candidates:
            raise ValueError(f"{path}: taxonomy candidate labels must be unique")
        seen_candidates.add(candidate)
        entries.append(TaxonomyEntry(id=label_id, name=name, candidate=candidate))
    return entries


def iter_jsonl_files(path: Path) -> list[Path]:
    if path.is_file():
        if path.suffix.lower() != ".jsonl":
            raise ValueError(f"Expected a .jsonl file, got: {path}")
        return [path]
    if path.is_dir():
        files = sorted(path.rglob("*.jsonl"))
        if not files:
            raise ValueError(f"No .jsonl files under: {path}")
        return files
    raise FileNotFoundError(path)


def resolve_output_path(*, input_root: Path, input_path: Path, output_base: Path) -> Path:
    rel = input_path.relative_to(input_root)
    return output_base / rel


def resolve_output_base(*, input_path: Path, output_root: str | None, output_arg: Path) -> Path:
    """Map --output-root to data/processed/<root>/<input-dir-name>/…"""
    if output_root:
        base = Path(output_root)
        if not base.is_absolute():
            base = PROCESSED / base
        if input_path.is_dir():
            return base / input_path.name
        return base / input_path.parent.name
    if input_path.is_dir():
        out_base = output_arg
        if out_base.suffix:
            out_base = out_base.parent / out_base.stem
        return out_base
    return output_arg.parent if output_arg.suffix else output_arg


def resolve_input_root(input_path: Path) -> Path:
    return input_path if input_path.is_dir() else input_path.parent


def iter_jsonl_rows(path: Path) -> Iterator[tuple[int, dict[str, Any]]]:
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            yield line_no, json.loads(line)


def _append_choice_lines(parts: list[str], row: dict[str, Any]) -> None:
    choices = row.get("choices")
    if isinstance(choices, list) and choices:
        parts.append("Choices:")
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for i, choice in enumerate(choices):
            pref = letters[i] if i < len(letters) else str(i)
            parts.append(f"  {pref}) {choice}")
        return
    if isinstance(choices, dict) and choices:
        parts.append("Choices:")
        for key, value in choices.items():
            parts.append(f"  {key}) {value}")
        return

    options = row.get("options")
    if isinstance(options, list) and options:
        parts.append("Options:")
        for opt in options:
            parts.append(f"  {opt}")
        return

    option_lines: list[str] = []
    for letter in "abcdefghijklmnopqrstuvwxyz":
        key = f"option_{letter}"
        if key in row and row[key] is not None:
            option_lines.append(f"  {letter.upper()}) {row[key]}")
    if option_lines:
        parts.append("Options:")
        parts.extend(option_lines)


def text_for_classification(row: dict[str, Any]) -> str:
    """Build classifier input from any JSONL object (dataset-agnostic)."""
    parts: list[str] = []
    for key in TEXT_KEYS:
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            parts.append(value.strip())
    _append_choice_lines(parts, row)

    labels = row.get("labels")
    if isinstance(labels, str) and labels.strip() and "sentence_1" in row:
        parts.append(f"Label: {labels.strip()}")

    if parts:
        return "\n\n".join(parts)
    return json.dumps(row, ensure_ascii=False)


def infer_source(input_path: Path) -> str:
    try:
        rel = input_path.relative_to(RAW_ROOT)
        parts = rel.parts
        if len(parts) >= 2:
            return "/".join(parts[:-1])
        return rel.as_posix()
    except ValueError:
        return input_path.stem


_LANG_RE = re.compile(r"(^|[/\\])(en|de|fr|es|it|pt|nl|pl|ru|zh|ja|ko)([/\\]|$)", re.I)


def infer_language(input_path: Path, row: dict[str, Any]) -> str:
    for key in ("language", "lang", "locale"):
        val = row.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip().lower()[:8]
    path_str = input_path.as_posix()
    m = _LANG_RE.search(path_str)
    if m:
        return m.group(2).lower()
    if re.search(r"(^|[/\\])(german|deutsch|supergleber|germeval)([/\\_]|$)", path_str, re.I):
        return "de"
    return "en"


def infer_task_type(row: dict[str, Any]) -> str:
    if "json_schema" in row and "question" not in row:
        return "code_configuration_analysis"
    if row.get("sentence_1") and row.get("sentence_2"):
        return "scenario_reasoning"
    if row.get("context") and row.get("question") and row.get("answers"):
        return "short_answer"
    if row.get("question") and (
        row.get("choices") or row.get("options") or row.get("option_a") or row.get("answer") is not None
    ):
        return "mcq_answering"
    if row.get("prompt") and row.get("code"):
        return "code_review"
    if row.get("question") or row.get("prompt"):
        return "open_explanation"
    return "open_explanation"


def _index_to_letter(index: int) -> str | None:
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if 0 <= index < len(letters):
        return letters[index]
    return None


def build_evaluation(row: dict[str, Any]) -> dict[str, Any] | None:
    if "answer" in row:
        ans = row["answer"]
        if isinstance(ans, int):
            letter = _index_to_letter(ans)
            if letter is not None:
                return {"scoring_type": "exact_match", "correct_answer": letter, "max_score": 1}
        if isinstance(ans, str) and ans.strip():
            return {"scoring_type": "exact_match", "correct_answer": ans.strip(), "max_score": 1}
    if "answers" in row and row["answers"] is not None:
        if isinstance(row["answers"], dict) and row["answers"].get("text"):
            texts = row["answers"]["text"]
            if isinstance(texts, list) and texts:
                return {"scoring_type": "exact_match", "correct_answer": texts[0], "max_score": 1}
        return {"scoring_type": "exact_match", "correct_answer": row["answers"], "max_score": 1}
    return None


def rank_scores(
    labels: list[str],
    scores: list[float],
    *,
    multi_label: bool,
) -> tuple[list[str], list[float]]:
    pairs = sorted(zip(labels, scores, strict=True), key=lambda item: item[1], reverse=True)
    if not multi_label:
        return [pairs[0][0]], [pairs[0][1]]
    top_score = pairs[0][1]
    threshold = 0.5 * top_score
    selected = [(label, score) for label, score in pairs if score >= threshold]
    return [label for label, _ in selected], [score for _, score in selected]


def softmax(values: list[float]) -> list[float]:
    if not values:
        return []
    max_val = max(values)
    exp_vals = [math.exp(v - max_val) for v in values]
    total = sum(exp_vals)
    return [v / total for v in exp_vals]


def _flash_attention_available() -> bool:
    try:
        import flash_attn  # noqa: F401

        return True
    except ImportError:
        return False


def _patch_llama_encoder_class(model_cls: type) -> None:
    """Allow Microsoft's LLM2CLIP encoder to load without flash-attn (sdpa fallback)."""
    if getattr(model_cls, "_scale_c_sdpa_patched", False):
        return

    import torch.nn as nn
    from transformers.modeling_layers import GradientCheckpointingLayer
    from transformers.models.llama.modeling_llama import (
        LlamaAttention,
        LlamaDecoderLayer,
        LlamaMLP,
        LlamaPreTrainedModel,
        LlamaRMSNorm,
        LlamaRotaryEmbedding,
    )

    class ModifiedLlamaAttention(LlamaAttention):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.is_causal = False

    class ModifiedLlamaDecoderLayer(LlamaDecoderLayer):
        def __init__(self, config, layer_idx: int):
            GradientCheckpointingLayer.__init__(self)
            self.hidden_size = config.hidden_size
            self.self_attn = ModifiedLlamaAttention(config=config, layer_idx=layer_idx)
            self.mlp = LlamaMLP(config)
            self.input_layernorm = LlamaRMSNorm(config.hidden_size, eps=config.rms_norm_eps)
            self.post_attention_layernorm = LlamaRMSNorm(
                config.hidden_size, eps=config.rms_norm_eps
            )

    def patched_init(self, config) -> None:
        LlamaPreTrainedModel.__init__(self, config)
        self.padding_idx = config.pad_token_id
        self.vocab_size = config.vocab_size
        self.embed_tokens = nn.Embedding(
            config.vocab_size, config.hidden_size, self.padding_idx
        )
        self.layers = nn.ModuleList(
            [
                ModifiedLlamaDecoderLayer(config, layer_idx)
                for layer_idx in range(config.num_hidden_layers)
            ]
        )
        self._use_sdpa = config._attn_implementation == "sdpa"
        self._use_flash_attention_2 = config._attn_implementation == "flash_attention_2"
        self.norm = LlamaRMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        self.rotary_emb = LlamaRotaryEmbedding(config=config)
        self.gradient_checkpointing = False
        self.post_init()

    model_cls.__init__ = patched_init
    model_cls._scale_c_sdpa_patched = True


class _LlamaEncoderSdpaFallback:
    """Patch HF dynamic import so LLM2CLIP loads with SDPA when flash-attn is missing."""

    _PATCH_TARGETS = (
        "transformers.dynamic_module_utils",
        "transformers.models.auto.auto_factory",
    )

    def __init__(self) -> None:
        self._originals: dict[str, Any] = {}

    def __enter__(self) -> None:
        if _flash_attention_available():
            return

        def get_class_patched(*args, **kwargs):
            original = self._originals["transformers.dynamic_module_utils"]
            cls = original(*args, **kwargs)
            if getattr(cls, "__name__", "") == "LlamaEncoderModel":
                _patch_llama_encoder_class(cls)
            return cls

        import importlib

        for target in self._PATCH_TARGETS:
            mod = importlib.import_module(target)
            self._originals[target] = mod.get_class_from_dynamic_module
            mod.get_class_from_dynamic_module = get_class_patched

    def __exit__(self, exc_type, exc, tb) -> None:
        if not self._originals:
            return
        import importlib

        for target, original in self._originals.items():
            importlib.import_module(target).get_class_from_dynamic_module = original


class Llm2ClipTextEncoder:
    """Minimal LLM2Vec-style mean pooling for LLM2CLIP text checkpoints."""

    def __init__(self, model, tokenizer, *, device: str, max_length: int = 512) -> None:
        self.model = model
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.device = device
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "left"
        self.model.config._name_or_path = "meta-llama/Meta-Llama-3-8B-Instruct"
        self.model.eval()

    def _format_text(self, text: str) -> str:
        messages = [{"role": "user", "content": text.strip()}]
        return self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False,
        )

    def encode(self, texts: list[str], *, batch_size: int = 8):
        import torch

        formatted = [self._format_text(text) for text in texts]
        embeddings: list[torch.Tensor] = []
        with torch.no_grad():
            for start in range(0, len(formatted), batch_size):
                batch_texts = formatted[start : start + batch_size]
                features = self.tokenizer(
                    batch_texts,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=self.max_length,
                ).to(self.device)
                hidden = self.model(**features).last_hidden_state
                lengths = features["attention_mask"].sum(dim=-1)
                batch_emb = torch.stack(
                    [hidden[i, -length:, :].mean(dim=0) for i, length in enumerate(lengths)],
                    dim=0,
                )
                batch_emb = torch.nn.functional.normalize(batch_emb, p=2, dim=1)
                embeddings.append(batch_emb)
        return torch.cat(embeddings, dim=0)


def load_llm2clip_text_encoder(model_id: str, device: str) -> Llm2ClipTextEncoder:
    import torch
    from transformers import AutoConfig, AutoModel, AutoTokenizer

    attn = "flash_attention_2" if _flash_attention_available() else "sdpa"
    config = AutoConfig.from_pretrained(model_id, trust_remote_code=True)
    load_kwargs = {
        "torch_dtype": torch.bfloat16 if device != "cpu" else torch.float32,
        "config": config,
        "trust_remote_code": True,
        "attn_implementation": attn,
    }
    with _LlamaEncoderSdpaFallback():
        model = AutoModel.from_pretrained(model_id, **load_kwargs)
    model = model.to(device)
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if attn == "sdpa" and not _flash_attention_available():
        print(
            "Note: flash-attn is not installed; loaded LLM2CLIP with SDPA attention.",
            file=sys.stderr,
        )
    return Llm2ClipTextEncoder(model, tokenizer, device=device)


class NLIBackend:
    method = "nli"

    def __init__(self, model_id: str, device: int | str) -> None:
        from transformers import pipeline

        self.model_id = model_id
        self._classifier = pipeline(
            "zero-shot-classification",
            model=model_id,
            device=device,
        )

    def classify(
        self,
        text: str,
        entries: list[TaxonomyEntry],
        *,
        multi_label: bool,
    ) -> tuple[list[str], list[float]]:
        candidates = [entry.candidate for entry in entries]
        result = self._classifier(text, candidates, multi_label=multi_label)
        return list(result["labels"]), [float(x) for x in result["scores"]]


class EmbeddingBackend:
    method = "embedding"

    def __init__(self, model_id: str, device: int | str) -> None:
        self.model_id = model_id
        self._device = torch_device(device)
        if "llm2clip" in model_id.casefold():
            self._encoder = load_llm2clip_text_encoder(model_id, self._device)
            self._kind = "llm2clip"
        else:
            from sentence_transformers import SentenceTransformer

            self._encoder = SentenceTransformer(model_id, trust_remote_code=True, device=self._device)
            self._kind = "sbert"

    def _encode(self, texts: list[str]):
        if self._kind == "llm2clip":
            return self._encoder.encode(texts)
        return self._encoder.encode(texts, convert_to_tensor=True, normalize_embeddings=True)

    def classify(
        self,
        text: str,
        entries: list[TaxonomyEntry],
        *,
        multi_label: bool,
    ) -> tuple[list[str], list[float]]:
        from sentence_transformers.util import cos_sim

        candidates = [entry.candidate for entry in entries]
        text_emb = self._encode([text])
        label_embs = self._encode(candidates)
        scores = cos_sim(text_emb, label_embs)[0].tolist()
        labels_out, scores_out = rank_scores(candidates, scores, multi_label=multi_label)
        if multi_label:
            return labels_out, scores_out
        ordered = sorted(zip(candidates, scores, strict=True), key=lambda item: item[1], reverse=True)
        return [label for label, _ in ordered], [score for _, score in ordered]


class GenerativeBackend:
    method = "generative"

    def __init__(self, model_id: str, device: int | str) -> None:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.model_id = model_id
        self._device = torch_device(device)
        dtype = torch.bfloat16 if self._device != "cpu" else torch.float32
        self._tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        self._model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=dtype,
            trust_remote_code=True,
        ).to(self._device)
        self._model.eval()

    @staticmethod
    def _system_prompt(entries: list[TaxonomyEntry]) -> str:
        lines = [
            "You are an expert tasked with classifying cybersecurity education content.",
            "",
            "# CLASS DEFINITIONS #",
            "",
            f"The {len(entries)} possible classes are:",
        ]
        for index, entry in enumerate(entries, start=1):
            description = entry.candidate.split(": ", 1)[-1]
            lines.append(f"{index} - {entry.name}: {description}")
        lines.extend(
            [
                "",
                "# RULES #",
                "- Assign exactly one class to the content.",
                "- Respond only with the exact label name (no explanation).",
            ]
        )
        return "\n".join(lines)

    def _chat_prefix(self, text: str, entries: list[TaxonomyEntry]) -> str:
        messages = [
            {"role": "system", "content": self._system_prompt(entries)},
            {
                "role": "user",
                "content": (
                    "Classify the following content into one taxonomy label.\n\n"
                    f"Content:\n{text}\n\n"
                    "Answer with the exact label name only."
                ),
            },
        ]
        return self._tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

    def _label_logprob(self, prefix: str, label: str) -> float:
        import torch

        suffix = label if prefix.endswith("\n") else f" {label}"
        full = prefix + suffix
        prefix_ids = self._tokenizer(prefix, add_special_tokens=False)["input_ids"]
        full_ids = self._tokenizer(full, add_special_tokens=False)["input_ids"]
        if len(full_ids) <= len(prefix_ids):
            return float("-inf")
        input_ids = torch.tensor([full_ids], device=self._device)
        with torch.no_grad():
            logits = self._model(input_ids=input_ids).logits[0]
        total = 0.0
        for pos in range(len(prefix_ids), len(full_ids)):
            token_id = full_ids[pos]
            total += torch.log_softmax(logits[pos - 1], dim=-1)[token_id].item()
        return total / max(len(full_ids) - len(prefix_ids), 1)

    def classify(
        self,
        text: str,
        entries: list[TaxonomyEntry],
        *,
        multi_label: bool,
    ) -> tuple[list[str], list[float]]:
        prefix = self._chat_prefix(text, entries)
        logprobs = [self._label_logprob(prefix, entry.name) for entry in entries]
        probs = softmax(logprobs)
        candidates = [entry.candidate for entry in entries]
        labels_out, scores_out = rank_scores(candidates, probs, multi_label=multi_label)
        if multi_label:
            return labels_out, scores_out
        ordered = sorted(zip(candidates, probs, strict=True), key=lambda item: item[1], reverse=True)
        return [label for label, _ in ordered], [score for _, score in ordered]


def build_backend(method: str, model_id: str, device: int | str) -> ClassifierBackend:
    if method == "nli":
        return NLIBackend(model_id, device)
    if method == "embedding":
        return EmbeddingBackend(model_id, device)
    if method == "generative":
        return GenerativeBackend(model_id, device)
    raise ValueError(f"Unknown method: {method}")


def prediction_from_result(
    entries: list[TaxonomyEntry],
    labels_out: list[str],
    scores_out: list[float],
) -> tuple[str, str, dict[str, float]]:
    by_candidate = {entry.candidate: entry for entry in entries}
    raw_scores: dict[str, float] = {}
    for candidate, score in zip(labels_out, scores_out, strict=True):
        entry = by_candidate[candidate]
        raw_scores[entry.id] = float(score)
    top = by_candidate[labels_out[0]]
    return top.id, top.name, raw_scores


def taxonomy_prediction(
    entries: list[TaxonomyEntry],
    labels_out: list[str],
    scores_out: list[float],
) -> dict[str, Any]:
    pred_id, pred_name, raw_scores = prediction_from_result(entries, labels_out, scores_out)
    return {
        "predicted_label": pred_id,
        "predicted_label_name": pred_name,
        "raw_scores": raw_scores,
    }


def load_extra_taxonomies(taxonomy_dir: Path, names: list[str]) -> dict[str, list[TaxonomyEntry]]:
    taxonomies: dict[str, list[TaxonomyEntry]] = {}
    for name in names:
        path = taxonomy_dir / f"{name}.json"
        if not path.is_file():
            raise FileNotFoundError(f"Taxonomy not found: {path}")
        taxonomies[name] = load_taxonomy(path)
    return taxonomies


def tier_number(label_name: Any) -> int:
    if not isinstance(label_name, str):
        return DEFAULT_TIER
    match = re.match(r"tier(\d+)_", label_name)
    if match:
        return int(match.group(1))
    return DEFAULT_TIER


def build_record(
    *,
    record_id: str,
    row: dict[str, Any],
    input_path: Path,
    model: str,
    method: str,
    pred_id: str,
    pred_name: str,
    raw_scores: dict[str, float],
    taxonomy_results: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    taxonomy_results = taxonomy_results or {}
    task_type = taxonomy_results.get("tasks", {}).get("predicted_label_name") or infer_task_type(row)
    difficulty = taxonomy_results.get("difficulty", {}).get("predicted_label_name", PLACEHOLDER)
    risk_category = taxonomy_results.get("risks", {}).get("predicted_label_name", PLACEHOLDER)
    cognitive_skill = taxonomy_results.get("cognitive", {}).get("predicted_label_name", PLACEHOLDER)
    tier = tier_number(taxonomy_results.get("tiers", {}).get("predicted_label_name"))

    record: dict[str, Any] = {
        "id": record_id,
        "benchmark": BENCHMARK,
        "version": SCHEMA_VERSION,
        "tier": tier,
        "task_type": task_type,
        "metadata": {
            "difficulty": difficulty,
            "source": infer_source(input_path),
            "language": infer_language(input_path, row),
            "risk_category": risk_category,
            "cognitive_skill": cognitive_skill,
        },
        "classification": {
            "predicted_label": pred_id,
            "predicted_label_name": pred_name,
            "raw_scores": raw_scores,
            "classifier": {"model": model, "method": method},
        },
        "payload": row,
    }
    if taxonomy_results:
        record["classification"]["taxonomies"] = taxonomy_results
    evaluation = build_evaluation(row)
    if evaluation is not None:
        record["evaluation"] = evaluation
    return record


def classify_files(
    *,
    input_files: list[Path],
    input_root: Path,
    output_writer,
    backend: ClassifierBackend,
    entries: list[TaxonomyEntry],
    extra_taxonomies: dict[str, list[TaxonomyEntry]],
    args: argparse.Namespace,
    next_id: int,
) -> tuple[int, int, int]:
    seen = 0
    written = 0
    for input_path in input_files:
        for _line_no, row in iter_jsonl_rows(input_path):
            if args.start > 0 and seen < args.start:
                seen += 1
                continue
            if args.max_rows is not None and written >= args.max_rows:
                return seen, written, next_id

            text = text_for_classification(row)
            labels_out, scores_out = backend.classify(
                text,
                entries,
                multi_label=args.multi_label,
            )
            pred_id, pred_name, raw_scores = prediction_from_result(entries, labels_out, scores_out)
            taxonomy_results: dict[str, dict[str, Any]] = {}
            for taxonomy_name, taxonomy_entries in extra_taxonomies.items():
                taxonomy_labels, taxonomy_scores = backend.classify(
                    text,
                    taxonomy_entries,
                    multi_label=False,
                )
                taxonomy_results[taxonomy_name] = taxonomy_prediction(
                    taxonomy_entries,
                    taxonomy_labels,
                    taxonomy_scores,
                )
            if taxonomy_results:
                for result in taxonomy_results.values():
                    result["classifier"] = {"model": backend.model_id, "method": backend.method}

            record_id = f"{args.id_prefix}_{next_id:06d}"
            next_id += 1
            record = build_record(
                record_id=record_id,
                row=row,
                input_path=input_path,
                model=backend.model_id,
                method=backend.method,
                pred_id=pred_id,
                pred_name=pred_name,
                raw_scores=raw_scores,
                taxonomy_results=taxonomy_results,
            )
            output_writer(record, input_path)
            seen += 1
            written += 1

        if args.max_rows is not None and written >= args.max_rows:
            break
    return seen, written, next_id


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"JSONL file or directory tree (default: {DEFAULT_INPUT}).",
    )
    parser.add_argument(
        "--taxonomy",
        type=Path,
        default=DEFAULT_TAXONOMY,
        help=f"Label taxonomy JSON (default: {DEFAULT_TAXONOMY}).",
    )
    parser.add_argument(
        "--taxonomy-dir",
        type=Path,
        default=DEFAULT_TAXONOMY_DIR,
        help=f"Directory with extra taxonomy JSON files (default: {DEFAULT_TAXONOMY_DIR}).",
    )
    parser.add_argument(
        "--extra-taxonomies",
        nargs="*",
        choices=("tasks", "risks", "difficulty", "cognitive", "tiers"),
        default=list(DEFAULT_EXTRA_TAXONOMIES),
        help=(
            "Extra taxonomies to classify into record fields. "
            "Use --extra-taxonomies with no values to disable."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=(
            f"Output JSONL file when --input is a single file without --output-root "
            f"(default: {DEFAULT_OUTPUT})."
        ),
    )
    parser.add_argument(
        "--output-root",
        default=DEFAULT_OUTPUT_ROOT,
        help=(
            "Write under data/processed/<output-root>/<input-folder-name>/, mirroring the "
            f"directory tree passed to --input (default: {DEFAULT_OUTPUT_ROOT}). "
            "Pass an empty string to disable and use --output instead."
        ),
    )
    parser.add_argument(
        "--method",
        choices=tuple(METHOD_DEFAULT_MODELS),
        default=DEFAULT_METHOD,
        help=(
            "Classification backend: nli (MNLI pipeline), embedding (cosine similarity), "
            f"or generative (prompted LLM). Default: {DEFAULT_METHOD}."
        ),
    )
    parser.add_argument(
        "--model",
        default=None,
        help=(
            "Model id for the selected --method. Defaults: "
            + ", ".join(f"{method}={model}" for method, model in METHOD_DEFAULT_MODELS.items())
        ),
    )
    parser.add_argument(
        "--multi-label",
        action=argparse.BooleanOptionalAction,
        default=DEFAULT_MULTI_LABEL,
        help="Allow multiple labels above 0.5 * top score.",
    )
    parser.add_argument(
        "--truncate",
        action=argparse.BooleanOptionalAction,
        default=DEFAULT_TRUNCATE,
        help="Overwrite output instead of appending.",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=DEFAULT_MAX_ROWS,
        help="Process at most this many non-empty JSONL rows (after --start), across all inputs.",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=DEFAULT_START,
        help="Skip the first N non-empty JSONL rows (global across all input files).",
    )
    parser.add_argument(
        "--id-prefix",
        default=DEFAULT_ID_PREFIX,
        help=f"Prefix for generated record ids (default: {DEFAULT_ID_PREFIX}).",
    )
    parser.add_argument(
        "--device",
        choices=("auto", "cpu", "cuda", "mps"),
        default="auto",
        help=(
            "Inference device. Use cpu when the NVIDIA driver is older than the PyTorch CUDA build "
            "(avoids CUDA init warnings). Default: auto (cuda if available, else mps, else cpu)."
        ),
    )
    parser.add_argument(
        "--gpu",
        type=int,
        default=DEFAULT_GPU,
        help=(
            "Physical GPU index for CUDA_VISIBLE_DEVICES (for example 0-3). "
            "The process always uses logical cuda:0 after masking."
        ),
    )
    args = parser.parse_args()

    if args.gpu is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu)

    if args.device == "cpu":
        os.environ["CUDA_VISIBLE_DEVICES"] = ""

    if not args.input.exists():
        raise SystemExit(
            f"Input not found: {args.input}\n"
            "Fetch data first or pass --input to an existing .jsonl file or directory."
        )
    if not args.taxonomy.is_file():
        raise SystemExit(f"Taxonomy not found: {args.taxonomy}")
    if args.extra_taxonomies and not args.taxonomy_dir.is_dir():
        raise SystemExit(f"Taxonomy directory not found: {args.taxonomy_dir}")

    method = args.method
    model = args.model or METHOD_DEFAULT_MODELS[method]
    inferred = infer_method(model)
    if inferred and inferred != method and args.model is not None:
        print(
            f"Note: model {model!r} looks like --method {inferred!r}; continuing with {method!r}.",
            file=sys.stderr,
        )
    model = resolve_model_id(model, method)

    try:
        input_files = iter_jsonl_files(args.input)
    except (FileNotFoundError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc

    try:
        entries = load_taxonomy(args.taxonomy)
        extra_taxonomies = load_extra_taxonomies(args.taxonomy_dir, args.extra_taxonomies)
    except (FileNotFoundError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc
    device = pick_device(args.device)
    backend = build_backend(method, model, device)

    output_root = args.output_root.strip() if args.output_root else None
    input_root = resolve_input_root(args.input)
    output_base = resolve_output_base(
        input_path=args.input,
        output_root=output_root,
        output_arg=args.output,
    )

    PROCESSED.mkdir(parents=True, exist_ok=True)
    next_id = 1

    use_tree_output = args.input.is_dir() or bool(output_root)

    if use_tree_output:
        output_base.mkdir(parents=True, exist_ok=True)

        handles: dict[Path, Any] = {}

        def output_writer(record: dict[str, Any], input_path: Path) -> None:
            if output_root or args.input.is_dir():
                out_path = resolve_output_path(
                    input_root=input_root,
                    input_path=input_path,
                    output_base=output_base,
                )
            else:
                out_path = args.output
            out_path.parent.mkdir(parents=True, exist_ok=True)
            if out_path not in handles:
                mode = "w" if args.truncate else "a"
                handles[out_path] = out_path.open(mode, encoding="utf-8")
            handles[out_path].write(json.dumps(record, ensure_ascii=False) + "\n")

        _, written, _ = classify_files(
            input_files=input_files,
            input_root=input_root,
            output_writer=output_writer,
            backend=backend,
            entries=entries,
            extra_taxonomies=extra_taxonomies,
            args=args,
            next_id=next_id,
        )
        for handle in handles.values():
            handle.close()

        out_display = output_base.relative_to(ROOT) if output_base.is_relative_to(ROOT) else output_base
        print(
            f"Wrote {written} record(s) under {out_display} "
            f"from {len(input_files)} file(s) "
            f"(method={method}, model={model}, device={device}, "
            f"extra_taxonomies={','.join(extra_taxonomies) or 'none'})"
        )
    else:
        mode = "w" if args.truncate else "a"

        def output_writer(record: dict[str, Any], _input_path: Path) -> None:
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")

        with args.output.open(mode, encoding="utf-8") as out_f:
            _, written, _ = classify_files(
                input_files=input_files,
                input_root=args.input,
                output_writer=output_writer,
                backend=backend,
                entries=entries,
                extra_taxonomies=extra_taxonomies,
                args=args,
                next_id=next_id,
            )

        out_display = args.output.relative_to(ROOT) if args.output.is_relative_to(ROOT) else args.output
        print(
            f"Wrote {written} record(s) to {out_display} "
            f"from {len(input_files)} file(s) "
            f"(method={method}, model={model}, device={device}, "
            f"extra_taxonomies={','.join(extra_taxonomies) or 'none'})"
        )


if __name__ == "__main__":
    main()
