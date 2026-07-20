#!/usr/bin/env python3
"""Generate Phase 1 benchmark visualizations (NLI + embedding classifiers).

Reads summaries from data/results/phase1/{nli,embedding}/
Writes figures to figures/phase1/analysis/
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "data" / "results" / "phase1"
OUT_DIR = ROOT / "figures" / "phase1" / "analysis"
TAXONOMY = ROOT / "schema" / "taxonomy.json"
COARSE = ROOT / "schema" / "taxonomy_coarse.json"

MODELS = [
    "roberta-base",
    "cybertuned",
    "llama-3.1-8b",
    "foundation-sec-8b",
    "mistral-7b-instruct-v0.2",
    "lily-cyber-7b",
    "zephyr-7b-beta",
    "zysec-7b",
    "qwen3-14b",
    "baronllm-v2",
    "llama-3.3-70b-instruct",
    "trendyol-cyber-70b",
]

DISPLAY = {
    "roberta-base": "RoBERTa",
    "cybertuned": "CyBERTuned",
    "llama-3.1-8b": "Llama 3.1 8B",
    "foundation-sec-8b": "Found-Sec 8B",
    "mistral-7b-instruct-v0.2": "Mistral 7B",
    "lily-cyber-7b": "Lily Cyber 7B",
    "zephyr-7b-beta": "Zephyr 7B",
    "zysec-7b": "ZySec 7B",
    "qwen3-14b": "Qwen3 14B",
    "baronllm-v2": "BaronLLM v2",
    "llama-3.3-70b-instruct": "Llama 3.3 70B",
    "trendyol-cyber-70b": "Trendyol 70B",
}

PAIRS = [
    ("roberta-base", "cybertuned", "Encoder control"),
    ("llama-3.1-8b", "foundation-sec-8b", "8B Llama"),
    ("mistral-7b-instruct-v0.2", "lily-cyber-7b", "7B Mistral"),
    ("zephyr-7b-beta", "zysec-7b", "7B Zephyr"),
    ("qwen3-14b", "baronllm-v2", "14B Qwen"),
    ("llama-3.3-70b-instruct", "trendyol-cyber-70b", "70B Llama"),
]

PAIR_COLORS = {
    "Encoder control": "#6c757d",
    "8B Llama": "#0d6efd",
    "7B Mistral": "#fd7e14",
    "7B Zephyr": "#6f42c1",
    "14B Qwen": "#20c997",
    "70B Llama": "#dc3545",
}

NLI_COLOR = "#2E86AB"
EMB_COLOR = "#A23B72"
BASE_COLOR = "#94a3b8"
FT_COLOR = "#1e293b"

plt.rcParams.update(
    {
        "figure.dpi": 150,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.labelsize": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)


def load_summary(corpus: str, model: str) -> dict | None:
    path = EVAL_DIR / corpus / f"{model}_summary.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def load_taxonomies() -> tuple[dict[str, str], list[dict]]:
    tax = json.loads(TAXONOMY.read_text())
    coarse = json.loads(COARSE.read_text())
    topic_names = {label["id"]: label["name"] for label in tax["labels"]}
    return topic_names, coarse["labels"]


def course_accuracy(summary: dict, member_ids: list[str]) -> tuple[float | None, int]:
    by_topic = summary.get("by_topic", {})
    correct = total = 0
    for mid in member_ids:
        if mid in by_topic:
            correct += by_topic[mid]["correct"]
            total += by_topic[mid]["total"]
    if total == 0:
        return None, 0
    return correct / total, total


def topic_accuracy(summary: dict, topic_id: str) -> tuple[float | None, int]:
    by_topic = summary.get("by_topic", {})
    if topic_id not in by_topic:
        return None, 0
    row = by_topic[topic_id]
    if row["total"] == 0:
        return None, 0
    return row["correct"] / row["total"], row["total"]


def save(fig: plt.Figure, name: str) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / name
    fig.savefig(path)
    plt.close(fig)
    return path


def fig01_global_comparison() -> Path:
  """Grouped bar: global accuracy, all models, NLI vs embedding."""
  nli = [load_summary("nli", m) for m in MODELS]
  emb = [load_summary("embedding", m) for m in MODELS]
  labels = [DISPLAY[m] for m in MODELS]
  nli_acc = [(s["accuracy"] * 100 if s else 0) for s in nli]
  emb_acc = [(s["accuracy"] * 100 if s else 0) for s in emb]

  x = np.arange(len(MODELS))
  w = 0.38
  fig, ax = plt.subplots(figsize=(14, 6))
  b1 = ax.bar(x - w / 2, nli_acc, w, label="NLI", color=NLI_COLOR, alpha=0.9)
  b2 = ax.bar(x + w / 2, emb_acc, w, label="Embedding", color=EMB_COLOR, alpha=0.9)

  ax.bar_label(b1, fmt="%.0f%%", padding=2, fontsize=7)
  ax.bar_label(b2, fmt="%.0f%%", padding=2, fontsize=7)
  ax.set_xticks(x)
  ax.set_xticklabels(labels, rotation=45, ha="right")
  ax.set_ylabel("Accuracy (%)")
  ax.set_ylim(0, 88)
  ax.set_title("eval_1 Global Accuracy — NLI vs Embedding Classifiers")
  ax.legend(loc="upper left")
  ax.axhline(21, color="#adb5bd", ls="--", lw=0.8, alpha=0.7)
  ax.text(len(MODELS) - 0.5, 22.5, "Encoder ceiling ~21%", fontsize=8, color="#6c757d")
  fig.text(
    0.5,
    -0.12,
    "† Llama 3.3 70B: NLI partial (n=327/573); embedding n=1353 vs n=847 for other models",
    ha="center",
    fontsize=8,
    color="#6c757d",
  )
  return save(fig, "01_global_nli_vs_embedding.png")


def fig02_classifier_scatter() -> Path:
  """Scatter: NLI accuracy vs embedding accuracy per model."""
  fig, ax = plt.subplots(figsize=(8, 8))
  for base, ft, pair_name in PAIRS:
    color = PAIR_COLORS[pair_name]
    for alias, marker, size in [(base, "o", 90), (ft, "^", 110)]:
      sn = load_summary("nli", alias)
      se = load_summary("embedding", alias)
      if not sn or not se:
        continue
      x, y = sn["accuracy"] * 100, se["accuracy"] * 100
      ax.scatter(x, y, c=color, s=size, marker=marker, edgecolors="white", linewidths=0.8, zorder=3)
      offset = (4, 4) if alias != "llama-3.3-70b-instruct" else (4, -12)
      ax.annotate(DISPLAY[alias], (x, y), textcoords="offset points", xytext=offset, fontsize=8)

  lims = [0, 85]
  ax.plot(lims, lims, "--", color="#dee2e6", lw=1, zorder=1)
  ax.set_xlim(0, 72)
  ax.set_ylim(0, 82)
  ax.set_xlabel("NLI-classified accuracy (%)")
  ax.set_ylabel("Embedding-classified accuracy (%)")
  ax.set_title("Classifier Divergence — Model Positions in NLI vs Embedding Space")
  handles = [
    mpatches.Patch(color=c, label=n) for n, c in PAIR_COLORS.items()
  ]
  ax.legend(handles=handles, loc="lower right", fontsize=8, title="Model family")
  circle = plt.Line2D([], [], marker="o", color="gray", ls="", markersize=8, label="Base")
  tri = plt.Line2D([], [], marker="^", color="gray", ls="", markersize=9, label="Fine-tuned")
  ax.legend(handles=handles + [circle, tri], loc="lower right", fontsize=7, title="Family / role")
  return save(fig, "02_classifier_divergence_scatter.png")


def fig03_pair_deltas() -> Path:
  """Horizontal bars: fine-tuning delta per pair, NLI and embedding."""
  pair_labels = []
  nli_deltas = []
  emb_deltas = []
  colors = []
  for base, ft, name in PAIRS:
    sb, sf = load_summary("nli", base), load_summary("nli", ft)
    eb, ef = load_summary("embedding", base), load_summary("embedding", ft)
    pair_labels.append(name)
    nli_deltas.append((sf["accuracy"] - sb["accuracy"]) * 100 if sb and sf else 0)
    emb_deltas.append((ef["accuracy"] - eb["accuracy"]) * 100 if eb and ef else 0)
    colors.append(PAIR_COLORS[name])

  y = np.arange(len(pair_labels))
  h = 0.35
  fig, ax = plt.subplots(figsize=(10, 6))
  ax.barh(y + h / 2, nli_deltas, h, label="NLI Δ (pp)", color=NLI_COLOR, alpha=0.85)
  ax.barh(y - h / 2, emb_deltas, h, label="Embedding Δ (pp)", color=EMB_COLOR, alpha=0.85)
  ax.axvline(0, color="#495057", lw=0.8)
  ax.set_yticks(y)
  ax.set_yticklabels(pair_labels)
  ax.set_xlabel("Fine-tuning delta (percentage points)")
  ax.set_title("Fine-Tuning Lift by Model Pair — Base → Domain-Adapted")
  ax.legend(loc="lower right")
  for i, (dn, de) in enumerate(zip(nli_deltas, emb_deltas)):
    ax.text(dn + (0.8 if dn >= 0 else -0.8), i + h / 2, f"{dn:+.1f}", va="center", ha="left" if dn >= 0 else "right", fontsize=8)
    ax.text(de + (0.8 if de >= 0 else -0.8), i - h / 2, f"{de:+.1f}", va="center", ha="left" if de >= 0 else "right", fontsize=8)
  return save(fig, "03_pair_finetuning_deltas.png")


def fig04_paired_base_ft() -> Path:
  """Six-panel or single figure: base vs FT bars per pair."""
  fig, axes = plt.subplots(2, 3, figsize=(14, 8), sharey=True)
  axes = axes.flatten()
  for ax, (base, ft, name) in zip(axes, PAIRS):
    sb_n = load_summary("nli", base)
    sf_n = load_summary("nli", ft)
    sb_e = load_summary("embedding", base)
    sf_e = load_summary("embedding", ft)
    vals = [
      sb_n["accuracy"] * 100,
      sf_n["accuracy"] * 100,
      sb_e["accuracy"] * 100,
      sf_e["accuracy"] * 100,
    ]
    labels = ["NLI\nbase", "NLI\nFT", "Emb\nbase", "Emb\nFT"]
    bar_colors = [NLI_COLOR, NLI_COLOR, EMB_COLOR, EMB_COLOR]
    alphas = [0.55, 1.0, 0.55, 1.0]
    bars = ax.bar(labels, vals, color=bar_colors, alpha=0.9)
    for b, a in zip(bars, alphas):
      b.set_alpha(a)
    ax.set_title(name, fontsize=10, color=PAIR_COLORS[name])
    ax.set_ylim(0, 82)
    ax.bar_label(bars, fmt="%.0f%%", fontsize=8, padding=2)
  fig.suptitle("Base vs Fine-Tuned Accuracy by Pair (eval_1)", fontsize=13, y=1.02)
  fig.tight_layout()
  return save(fig, "04_paired_base_vs_finetuned.png")


def _heatmap_matrix(
    corpus: str,
    row_labels: list[str],
    row_ids: list[str],
    col_models: list[str],
    *,
    agg: str,
    coarse_labels: list[dict] | None = None,
    topic_names: dict[str, str] | None = None,
) -> np.ndarray:
  matrix = np.full((len(row_ids), len(col_models)), np.nan)
  for j, model in enumerate(col_models):
    summary = load_summary(corpus, model)
    if not summary:
      continue
    for i, rid in enumerate(row_ids):
      if agg == "topic":
        acc, n = topic_accuracy(summary, rid)
      else:
        members = next(c["members"] for c in coarse_labels if c["id"] == rid)
        acc, n = course_accuracy(summary, members)
      if acc is not None and n >= 3:
        matrix[i, j] = acc * 100
  return matrix


def fig05_course_heatmaps(topic_names: dict, coarse_labels: list[dict]) -> Path:
  course_names = [c["name"] for c in coarse_labels]
  course_ids = [c["id"] for c in coarse_labels]
  # Use display order: pairs grouped
  col_models = MODELS
  col_labels = [DISPLAY[m] for m in col_models]

  fig, axes = plt.subplots(1, 2, figsize=(18, 5.5))
  for ax, corpus, title in zip(
    axes,
    ["nli", "embedding"],
    ["NLI-classified", "Embedding-classified"],
  ):
    mat = _heatmap_matrix(corpus, course_names, course_ids, col_models, agg="course", coarse_labels=coarse_labels)
    im = ax.imshow(mat, aspect="auto", cmap="RdYlGn", vmin=10, vmax=85)
    ax.set_xticks(np.arange(len(col_labels)))
    ax.set_xticklabels(col_labels, rotation=55, ha="right", fontsize=8)
    ax.set_yticks(np.arange(len(course_names)))
    ax.set_yticklabels(course_names, fontsize=9)
    ax.set_title(f"{title} — Course Accuracy (%)")
    for i in range(mat.shape[0]):
      for j in range(mat.shape[1]):
        if not np.isnan(mat[i, j]):
          txt_color = "white" if mat[i, j] < 45 or mat[i, j] > 72 else "black"
          ax.text(j, i, f"{mat[i, j]:.0f}", ha="center", va="center", fontsize=7, color=txt_color)
  fig.colorbar(im, ax=axes, shrink=0.6, label="Accuracy (%)")
  fig.suptitle("Course-by-Course Performance (taxonomy_coarse.json)", fontsize=13, y=1.03)
  fig.tight_layout()
  return save(fig, "05_course_heatmap_nli_embedding.png")


def fig06_topic_delta_heatmaps(topic_names: dict) -> Path:
  """Per-pair topic delta heatmaps (fine-tuned minus base)."""
  topic_ids = sorted(topic_names.keys())
  short_names = [topic_names[t][:22] for t in topic_ids]

  fig, axes = plt.subplots(2, 3, figsize=(16, 14))
  axes = axes.flatten()
  vmin, vmax = -35, 35
  last_im = None
  for ax, (base, ft, name) in zip(axes, PAIRS):
    sn_b, sn_f = load_summary("nli", base), load_summary("nli", ft)
    se_b, se_f = load_summary("embedding", base), load_summary("embedding", ft)
    deltas = []
    for tid in topic_ids:
      bn, bf = topic_accuracy(sn_b, tid)[0], topic_accuracy(sn_f, tid)[0]
      en, ef = topic_accuracy(se_b, tid)[0], topic_accuracy(se_f, tid)[0]
      # average NLI and embedding delta where both exist
      ds = []
      if bn is not None and bf is not None:
        ds.append((bf - bn) * 100)
      if en is not None and ef is not None:
        ds.append((ef - en) * 100)
      deltas.append(np.mean(ds) if ds else np.nan)
    mat = np.array(deltas).reshape(-1, 1)
    last_im = ax.imshow(mat, aspect="auto", cmap="RdBu", vmin=vmin, vmax=vmax)
    ax.set_title(name, color=PAIR_COLORS[name], fontsize=10)
    ax.set_xticks([0])
    ax.set_xticklabels(["Δ avg"], fontsize=8)
    ax.set_yticks(np.arange(0, len(short_names), 3))
    ax.set_yticklabels([short_names[i] for i in range(0, len(short_names), 3)], fontsize=6)
  fig.colorbar(last_im, ax=axes, shrink=0.5, label="Avg Δ (pp) NLI+Embedding")
  fig.suptitle("Topic-Level Fine-Tuning Delta (Base → Fine-Tuned)", fontsize=13, y=1.01)
  fig.tight_layout()
  return save(fig, "06_topic_finetuning_delta_by_pair.png")


def fig07_llama33_topic_profile(topic_names: dict) -> Path:
  """Dedicated Llama 3.3 70B topic bars — NLI and embedding."""
  sn = load_summary("nli", "llama-3.3-70b-instruct")
  se = load_summary("embedding", "llama-3.3-70b-instruct")
  topic_ids = sorted(topic_names.keys())
  names = [topic_names[t] for t in topic_ids]
  nli_vals = []
  emb_vals = []
  for tid in topic_ids:
    a, _ = topic_accuracy(sn, tid)
    nli_vals.append(a * 100 if a is not None else np.nan)
    a, _ = topic_accuracy(se, tid)
    emb_vals.append(a * 100 if a is not None else np.nan)

  y = np.arange(len(topic_ids))
  h = 0.4
  fig, ax = plt.subplots(figsize=(11, 14))
  ax.barh(y - h / 2, nli_vals, h, label="NLI (partial)", color=NLI_COLOR, alpha=0.85)
  ax.barh(y + h / 2, emb_vals, h, label="Embedding", color=EMB_COLOR, alpha=0.85)
  ax.set_yticks(y)
  ax.set_yticklabels(names, fontsize=7)
  ax.set_xlabel("Accuracy (%)")
  ax.set_xlim(0, 105)
  ax.set_title("Llama 3.3 70B Instruct — Topic Accuracy on eval_1")
  ax.legend(loc="lower right")
  ax.axvline(50, color="#dee2e6", ls="--", lw=0.8)
  fig.text(0.01, 0.01, "NLI: n=327 (partial run). Embedding: n=1353.", fontsize=8, color="#6c757d")
  return save(fig, "07_llama33_70b_topic_profile.png")


def fig08_weakest_courses(coarse_labels: list[dict]) -> Path:
  """Avg accuracy per course across all models."""
  fig, axes = plt.subplots(1, 2, figsize=(12, 5))
  course_names = [c["name"] for c in coarse_labels]
  for ax, corpus in zip(axes, ["nli", "embedding"]):
    avgs = []
    for c in coarse_labels:
      accs = []
      for m in MODELS:
        s = load_summary(corpus, m)
        if s:
          a, n = course_accuracy(s, c["members"])
          if a is not None:
            accs.append(a * 100)
      avgs.append(np.mean(accs) if accs else 0)
    order = np.argsort(avgs)
    sorted_names = [course_names[i] for i in order]
    sorted_avgs = [avgs[i] for i in order]
    colors = plt.cm.RdYlGn(np.linspace(0.25, 0.85, len(sorted_avgs)))
    ax.barh(sorted_names, sorted_avgs, color=colors)
    ax.set_xlabel("Mean accuracy across 12 models (%)")
    ax.set_title(f"{corpus.upper()} — Weakest courses (lowest avg)")
    ax.set_xlim(0, 55)
    for i, v in enumerate(sorted_avgs):
      ax.text(v + 0.5, i, f"{v:.1f}%", va="center", fontsize=8)
  fig.suptitle("Course Difficulty on eval_1 (Average Across All Models)", fontsize=12)
  fig.tight_layout()
  return save(fig, "08_course_difficulty_average.png")


def fig09_encoder_vs_generative() -> Path:
  """Encoder pair vs generative model spectrum."""
  enc_models = ["roberta-base", "cybertuned"]
  gen_models = [m for m in MODELS if m not in enc_models]
  fig, ax = plt.subplots(figsize=(10, 5))
  x = np.arange(2)
  w = 0.08
  for i, m in enumerate(gen_models):
    sn = load_summary("nli", m)
    se = load_summary("embedding", m)
    nli_a = sn["accuracy"] * 100 if sn else 0
    emb_a = se["accuracy"] * 100 if se else 0
    is_ft = m in {ft for _, ft, _ in PAIRS}
    color = FT_COLOR if is_ft else BASE_COLOR
    ax.scatter(0, nli_a, s=60, c=color, alpha=0.7, zorder=2)
    ax.scatter(1, emb_a, s=60, c=color, alpha=0.7, zorder=2)
  # encoder band
  for corpus_idx, corpus in enumerate(["nli", "embedding"]):
    accs = [load_summary(corpus, m)["accuracy"] * 100 for m in enc_models]
    ax.fill_between(
      [corpus_idx - 0.15, corpus_idx + 0.15],
      min(accs) - 1,
      max(accs) + 1,
      color="#e9ecef",
      alpha=0.8,
      zorder=1,
    )
  ax.set_xticks([0, 1])
  ax.set_xticklabels(["NLI", "Embedding"])
  ax.set_ylabel("Accuracy (%)")
  ax.set_title("Encoder Control (shaded band) vs Generative Models")
  ax.set_xlim(-0.4, 1.4)
  ax.set_ylim(0, 80)
  base_patch = mpatches.Patch(color=BASE_COLOR, label="Generative base")
  ft_patch = mpatches.Patch(color=FT_COLOR, label="Generative fine-tuned")
  enc_patch = mpatches.Patch(color="#e9ecef", label="RoBERTa / CyBERTuned band")
  ax.legend(handles=[enc_patch, base_patch, ft_patch], loc="upper left")
  return save(fig, "09_encoder_vs_generative.png")


def fig10_70b_comparison(coarse_labels: list[dict]) -> Path:
  """70B base vs FT vs best 7B/8B on courses."""
  courses = [c["name"] for c in coarse_labels]
  base = load_summary("embedding", "llama-3.3-70b-instruct")
  ft = load_summary("embedding", "trendyol-cyber-70b")
  lily = load_summary("embedding", "lily-cyber-7b")
  llama8 = load_summary("embedding", "llama-3.1-8b")

  def course_accs(summary):
    return [course_accuracy(summary, c["members"])[0] * 100 for c in coarse_labels]

  fig, ax = plt.subplots(figsize=(11, 5.5))
  x = np.arange(len(courses))
  w = 0.2
  ax.bar(x - 1.5 * w, course_accs(base), w, label="Llama 3.3 70B (base)", color="#dc3545", alpha=0.85)
  ax.bar(x - 0.5 * w, course_accs(ft), w, label="Trendyol 70B (FT)", color="#fd7e14", alpha=0.85)
  ax.bar(x + 0.5 * w, course_accs(lily), w, label="Lily Cyber 7B (FT)", color="#20c997", alpha=0.85)
  ax.bar(x + 1.5 * w, course_accs(llama8), w, label="Llama 3.1 8B (base)", color="#0d6efd", alpha=0.85)
  ax.set_xticks(x)
  ax.set_xticklabels(courses, rotation=30, ha="right", fontsize=9)
  ax.set_ylabel("Embedding accuracy (%)")
  ax.set_title("Scale vs Domain Fine-Tuning — Embedding Classifier by Course")
  ax.legend(loc="upper right", fontsize=8)
  ax.set_ylim(0, 95)
  return save(fig, "10_scale_vs_finetune_embedding_courses.png")


def fig11_reasoning_topics(topic_names: dict) -> Path:
  reasoning_ids = ["SCLC00701", "SCLC01601", "SCLC02001", "SCLC02101"]
  names = [topic_names[t] for t in reasoning_ids]
  models = [
    "qwen3-14b",
    "baronllm-v2",
    "llama-3.1-8b",
    "foundation-sec-8b",
    "llama-3.3-70b-instruct",
    "trendyol-cyber-70b",
  ]
  fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
  for ax, corpus in zip(axes, ["nli", "embedding"]):
    x = np.arange(len(reasoning_ids))
    w = 0.12
    for i, m in enumerate(models):
      vals = []
      for tid in reasoning_ids:
        s = load_summary(corpus, m)
        a, _ = topic_accuracy(s, tid)
        vals.append((a or 0) * 100)
      ax.bar(x + (i - len(models) / 2) * w + w / 2, vals, w, label=DISPLAY[m], alpha=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=15, ha="right", fontsize=9)
    ax.set_ylabel("Accuracy (%)")
    ax.set_title(corpus.upper())
    ax.set_ylim(0, 78)
  handles, labels = axes[0].get_legend_handles_labels()
  fig.legend(handles, labels, loc="upper center", ncol=3, fontsize=8, bbox_to_anchor=(0.5, 1.08))
  fig.suptitle("Reasoning-Heavy Topics — Qwen vs Llama Scale", fontsize=12, y=1.12)
  fig.tight_layout()
  return save(fig, "11_reasoning_topics_comparison.png")


def fig12_pair_topic_heatmap_embedding() -> Path:
  """Full topic x model heatmap for embedding (key models only)."""
  topic_names, _ = load_taxonomies()
  key_models = [
    "roberta-base",
    "llama-3.1-8b",
    "foundation-sec-8b",
    "lily-cyber-7b",
    "qwen3-14b",
    "baronllm-v2",
    "llama-3.3-70b-instruct",
    "trendyol-cyber-70b",
  ]
  topic_ids = sorted(topic_names.keys())
  row_names = [topic_names[t][:24] for t in topic_ids]
  mat = _heatmap_matrix("embedding", row_names, topic_ids, key_models, agg="topic")
  fig, ax = plt.subplots(figsize=(12, 14))
  im = ax.imshow(mat, aspect="auto", cmap="RdYlGn", vmin=5, vmax=95)
  ax.set_xticks(np.arange(len(key_models)))
  ax.set_xticklabels([DISPLAY[m] for m in key_models], rotation=45, ha="right", fontsize=9)
  ax.set_yticks(np.arange(0, len(row_names), 2))
  ax.set_yticklabels([row_names[i] for i in range(0, len(row_names), 2)], fontsize=7)
  ax.set_title("Embedding Topic × Model Heatmap (eval_1)")
  fig.colorbar(im, ax=ax, shrink=0.4, label="Accuracy (%)")
  return save(fig, "12_embedding_topic_model_heatmap.png")


def main() -> None:
  topic_names, coarse_labels = load_taxonomies()
  paths = [
    fig01_global_comparison(),
    fig02_classifier_scatter(),
    fig03_pair_deltas(),
    fig04_paired_base_ft(),
    fig05_course_heatmaps(topic_names, coarse_labels),
    fig06_topic_delta_heatmaps(topic_names),
    fig07_llama33_topic_profile(topic_names),
    fig08_weakest_courses(coarse_labels),
    fig09_encoder_vs_generative(),
    fig10_70b_comparison(coarse_labels),
    fig11_reasoning_topics(topic_names),
    fig12_pair_topic_heatmap_embedding(),
  ]
  print(f"Wrote {len(paths)} figures to {OUT_DIR}/")
  for p in paths:
    print(f"  {p.relative_to(ROOT)}")


if __name__ == "__main__":
  main()
