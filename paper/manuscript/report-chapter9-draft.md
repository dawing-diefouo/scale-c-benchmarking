# Chapter 9 — Classifier stability (NLI vs embedding)

Replace **Section 9** in `Scale-C_Final_Report (1).docx`.  
Citations **[9]**, **[10]**, **[11]** — see `report-references.md`.  
**Shorter chapter** — methodological point for RQ2, not a second results dump.

**Proposed title (replaces “Classifier Divergence”):**

> **9. When we change the topic labeler, does the winner change?**

---

## 9. When we change the topic labeler, does the winner change?

Sections 6–8 already run every analysis **twice**: once with NLI topic labels, once with embedding labels [9], [10]. This section asks whether that choice matters for Scale-C model selection.

**Short answer:** Usually not much for **overall rankings**—but it matters a lot for the **70B pair** and for a handful of topics. If a recommendation flips when we change the labeler, we should not treat it as settled.

### 9.1 Global rankings mostly agree

On `data/eval_1`, all twelve models rank similarly under NLI and embedding (Spearman ρ ≈ **0.97**). The bottom (Qwen3, encoders) and top tier (70B models, Llama 3.1, Lily) are stable.

The important exception is **who leads**:

| Classifier view | #1 model | Accuracy |
|-----------------|----------|----------|
| NLI | Trendyol Cyber 70B | 65.1% |
| Embedding | Llama 3.3 70B | 75.7% † |

† Different item counts for Llama 3.3 embedding (Section 6.2).

So we do not have one undisputed Phase 1 champion—we have two leaders on two related but not identical corpora.

### 9.2 The 70B pair: opposite fine-tuning verdicts

Section 7 flagged this; here is the classifier angle.

| View | Llama 3.3 base | Trendyol | Δ |
|------|----------------|----------|---|
| NLI | 55.7% (partial) | 65.1% | **+9.4 pp** → fine-tuning “wins” |
| Embedding | 75.7% | 68.5% | **−7.2 pp** → base “wins” |

Same two models, same broad benchmark sources [11], different topic assignments and (for Llama 3.3) different evaluation completeness. **Trendyol cannot be called an unambiguous upgrade over Llama 3.3** until both are re-run on a frozen, shared item set.

At **topic level** for this pair (fine-tuning Δ direction, min n = 5 per side): **10 topics agree**, **12 disagree** (22 topics with enough support). That is the highest disagreement among all six pairs; e.g. Mistral→Lily agrees on ~24 of 29 comparable topics. Section 8 gave examples: Trendyol gains on “Other” and domains under NLI but loses on social engineering under embedding.

### 9.3 Why this happens (without picking a winner)

We treat NLI and embedding as **complementary views**, not duplicate metrics:

- **NLI labeling** scores whether item text *entails* a topic description [9]. Models whose answers track narrow cyber phrasing may look better when items are bucketed that way.
- **Embedding labeling** assigns topics by semantic similarity [10]. A large, lightly specialized base (Llama 3.3) may keep broader coverage that still matches embedding-defined topics—even when a heavily fine-tuned variant picks up entailment-friendly wording.

Neither view is “ground truth” for Scale-C curriculum labels. Human-reviewed topic tags on a fixed gold set would be the only arbiter; we did not have that at Phase 1 scale.

### 9.4 Implication for Scale-C

1. **Do not pick a model from one column of Table 6.1.** Check both views, or fix one labeling pipeline before deployment.
2. **Treat the 70B decision as open** until same-item re-evaluation.
3. **Pairwise claims need a classifier footnote**—especially Lily (mostly stable) vs Trendyol (not).
4. **Multi-view evaluation is a feature of this study**, not a bug: if rankings were identical everywhere, a single cheap labeler would suffice. They are not.

### 9.5 Figure

**[F13] Model positions in NLI vs embedding accuracy space**

![Figure F13 — Classifier divergence scatter](../../figures/eval_1/analysis/02_classifier_divergence_scatter.png)

*Caption:* Each point is one model; x = NLI accuracy, y = embedding accuracy. Points near the diagonal agree across views; offset points do not. The 70B pair (red) shows the largest spread between base (circle) and fine-tuned (triangle). Family colors match Section 7. Source: `data/eval_1`.

**[F14] (optional)** Re-use **Figure F12** (`06_topic_finetuning_delta_by_pair.png`) — side-by-side NLI/embedding topic Δ panels show *where* directions disagree, especially for Llama 3.3 → Trendyol.

### 9.6 RQ2

> When we assign items to Scale-C topics with NLI versus embeddings, do model rankings stay stable?

**Mostly yes** at global rank (ρ ≈ 0.97). **No** for (a) who is #1, (b) whether Trendyol beats its base, and (c) ~half of fine-grained topics in the 70B pair. Scale-C should not ignore RQ2 when writing the final model recommendation.

---

## References

| Ref | Used for |
|-----|----------|
| [9] | NLI zero-shot topic labeling |
| [10] | Embedding topic labeling |
| [11] | Shared benchmark pool, classifier-specific builds |

---

## Author notes (remove from thesis)

- Update §9.2 counts if Llama 3.3 NLI is completed.
- Section 10 (reasoning vs scale) can stay separate; do not duplicate Qwen3/Baron topic tables here.
- ~2 pages in Word is enough for this chapter.
