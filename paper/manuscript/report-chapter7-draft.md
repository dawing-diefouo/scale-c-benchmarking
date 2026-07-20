# Chapter 7 — Pairwise fine-tuning effects

Replace **Section 7** in `Scale-C_Final_Report (1).docx`.  
Citations **[1]–[7]**, **[8]** — see `report-references.md`.  
Tone matches `report-chapter6-draft.md` and `report-abstract-intro-draft.md`.

**Proposed section title (replaces “Pairwise Fine-Tuning Effects”):**

> **7. Did fine-tuning actually help? Pairwise comparisons**

Section 6 ranked models by absolute score. Scale-C needs a different question: **did the cybersecurity adaptation step improve anything compared with the base we would have used anyway?** That is what this chapter answers.

---

## 7. Did fine-tuning actually help? Pairwise comparisons

Table 6.1 showed that some cyber-branded models score well in absolute terms. It also hid an awkward fact: several of them score **below** their own base model once you line the pairs up properly.

For each of the six families in Table 5.1, we compute:

Δ = accuracy(fine-tuned) − accuracy(base)

on the same classifier corpus (NLI or embedding). Positive Δ means the adaptation helped on Tier 1 MCQ. Negative Δ means we would have been better off keeping the base [1], [8].

All values come from `data/eval_1/`. They are Phase 1 numbers only—no H5P or German tiers yet.

### 7.1 Summary: three buckets, not one story

Fine-tuning is **not** a uniform win. After looking at all six pairs, we group them like this:

| Bucket | Pairs | NLI Δ | Embedding Δ | Scale-C read (Phase 1) |
|--------|-------|-------|-------------|-------------------------|
| **Clear help** | Mistral → Lily; Qwen3 → Baron | +7.0; +14.3 | +6.8; +16.9 | Cyber SFT clearly moved the needle. Lily is a plausible 7B shortlist candidate; Baron rescues a weak base but still lands mid-pack in absolute terms (Table 6.1). |
| **Clear harm** | Llama 3.1 → Foundation-Sec; Zephyr → ZySec | −5.8; −10.8 | −8.7; −7.2 | For Tier 1 MCQ, the base models win. We would not pick these fine-tunes over their bases without new evidence from Tier 2/3. |
| **Mixed or marginal** | RoBERTa → CyBERTuned; Llama 3.3 → Trendyol | +0.5; +9.4 | +0.4; −7.2 | Encoder gain is tiny. The 70B pair **flips sign** between classifiers—treat as inconclusive until the base NLI run finishes and both sides use the same item set (Section 9). |

**Table 7.1 — Pairwise fine-tuning deltas (`data/eval_1`)**

| Pair | Training style | Base (NLI / Emb.) | Fine-tuned (NLI / Emb.) | Δ NLI | Δ Emb. | Verdict |
|------|----------------|-------------------|---------------------------|-------|--------|---------|
| RoBERTa → CyBERTuned | Encoder domain SFT [6] | 21.1% / 26.7% | 21.6% / 27.0% | +0.5 pp | +0.4 pp | Marginal; not a Scale-C path |
| Llama 3.1 → Foundation-Sec | Domain pretrain [2] | 57.9% / 60.9% | 52.2% / 52.2% | −5.8 pp | −8.7 pp | Consistent regression |
| Mistral → Lily | Instruct SFT [3] | 44.5% / 46.9% | 51.5% / 53.7% | +7.0 pp | +6.8 pp | Consistent gain |
| Zephyr → ZySec | Assistant tuning [4] | 37.9% / 43.2% | 27.1% / 36.0% | −10.8 pp | −7.2 pp | Largest consistent loss |
| Qwen3 → Baron | Instruct SFT [3] | 11.9% / 13.9% | 26.2% / 30.8% | +14.3 pp | +16.9 pp | Large lift from weak base |
| Llama 3.3 → Trendyol | Large SFT [3] | 55.7%† / 75.7%‡ | 65.1% / 68.5% | +9.4 pp | −7.2 pp | Classifier split |

† Llama 3.3 base NLI: partial run (182/327 of 573 items).  
‡ Embedding denominators differ (base 1353 vs fine-tuned 847)—see Section 6.2.

The main lesson for Scale-C is blunt: **“cybersecurity fine-tuned” on the model card is not proof it will do better on our benchmark** [7]. Two pairs improved on both views. Two got worse on both. The rest need more careful reading.

### 7.2 Pair-by-pair notes

#### RoBERTa → CyBERTuned (encoder control)

CyBERTuned adds about half a percentage point on NLI and less than half a point on embedding [6]. That is statistically noise at this scale, and it does not change the picture from Section 6: encoder models sit near 21–27% while generative 7B models jump by thirty-plus points.

For Scale-C this pair is a **sanity check**, not a candidate. We are not going to serve H5P or explanations through a choice-ranking encoder.

#### Llama 3.1 8B → Foundation-Sec-8B

Foundation-Sec was trained with continued domain pretraining on security text [2], [7]. In theory that should improve vocabulary and topic coverage. In practice, Tier 1 MCQ accuracy **drops** by 5.8 pp (NLI) and 8.7 pp (embedding).

One plausible explanation, consistent with the KL-forgetting discussion in Section 2 [4]: the model may have absorbed domain phrasing while **disturbing the answer patterns** Llama 3.1 had already learned for multiple-choice prompts. For Scale-C, the practical implication is simple—**on Phase 1 evidence, Llama 3.1 8B is the safer pick** in this family unless Tier 2/3 runs show a compensating advantage we have not measured yet.

#### Mistral 7B → Lily-Cybersecurity-7B

Lily is the cleanest success story in the 7B class. Both classifiers show roughly **+7 pp**. The fine-tuned model ends at 51.5% (NLI) and 53.7% (embedding)—not the global leader, but a solid move from a mid-40s base.

For a university project that may need local or modest-GPU hosting, **Mistral → Lily is the strongest “adaptation was worth it” signal** among the smaller generative pairs. It stays on the shortlist for Tier 2 H5P testing.

#### Zephyr 7B → ZySec-7B

ZySec shows the **largest consistent regression**: −10.8 pp NLI, −7.2 pp embedding. The base Zephyr is already mediocre on this benchmark; the fine-tuned model is worse still (27.1% NLI).

Assistant-style cyber tuning [4] may optimize for helpful chat tone without preserving MCQ reliability. Scale-C should **not** assume ZySec is an upgrade over Zephyr—or over other 7B options—for quiz-related tasks.

#### Qwen3 14B → BaronLLM v2

Baron’s deltas look dramatic (+14.3 / +16.9 pp), but context matters. Qwen3’s base scores are **unusually low** (11.9% NLI, 13.9% embedding)—likely a bad fit between Qwen3’s default chat template and our MCQ extraction setup, not proof that Qwen3 is useless in general [7].

Baron roughly **doubles** the base score and lands near 26–31% overall. That is real recovery, but Baron is still **not** a top-tier absolute performer (compare Lily or Llama 3.1 in Table 6.1). Fine-tuning fixed a broken baseline more than it built a new leader.

For Scale-C: Baron is interesting if we want a **mid-size cyber model** and can confirm the Qwen3 base was mis-served in our pipeline. It is not automatic front-runner material on Phase 1 MCQ alone.

#### Llama 3.3 70B → Trendyol Cybersecurity LLM v2 70B

This is the puzzling pair. Under NLI, Trendyol leads the whole study at 65.1% and beats its base by **+9.4 pp**—but that base NLI run is **incomplete** (327 items). Under embedding, Trendyol is still strong at 68.5% absolute yet **loses 7.2 pp** to the base because Llama 3.3 was scored on a larger, mixed task corpus (1,353 items).

We cannot recommend Trendyol over Llama 3.3 for Scale-C from these deltas alone. Section 9 treats the classifier split in more depth. Before any 70B deployment decision, we need a **finished, same-item re-evaluation** of both models.

### 7.3 Figures

**[F8] Fine-tuning delta by pair (NLI vs embedding)**

![Figure F8 — Fine-tuning deltas](../../figures/eval_1/analysis/03_pair_finetuning_deltas.png)

*Caption:* Horizontal bars show Δ (percentage points) for each base → fine-tuned family. Blue: NLI topic view; magenta: embedding topic view. Positive bars (right): adaptation helped. Negative bars (left): base was better. The Llama 3.3 → Trendyol row is the only pair with opposite signs. Source: `data/eval_1/*/ *_summary.json`.

**[F8b] Base vs fine-tuned accuracy within each pair**

![Figure F8b — Base vs fine-tuned by pair](../../figures/eval_1/analysis/04_paired_base_vs_finetuned.png)

*Caption:* Six small multiples—one per pair—with faded bars for bases and solid bars for fine-tuned models, under NLI and embedding. Easier to read than deltas alone when absolute level matters (e.g. Baron still below Lily despite a large Δ). Optional in the Word doc if space is tight; otherwise fold into F8 caption as a second panel reference.

### 7.4 What this means for Scale-C (Phase 1 only)

If we had to narrow the field **today**, using only Tier 1 MCQ and pairwise logic:

1. **Keep investigating:** Lily (best 7B adaptation story), Llama 3.1 8B base (beats Foundation-Sec), and—pending a clean re-run—the 70B Llama/Trendyol line.
2. **Deprioritize for MCQ:** Foundation-Sec, ZySec, and encoder-only paths.
3. **Treat with caution:** Baron (good Δ, modest absolute score; check Qwen3 serving), Trendyol (classifier split and incomplete base NLI).

None of these choices carry over to H5P JSON validity, German content, or safety until we run Tiers 2 and 3. A model that wins on Δ here could still fail when we ask for structured activity JSON.

### 7.5 Research question RQ1

> Does cybersecurity domain fine-tuning consistently improve benchmark performance, or is the effect pair-dependent?

**Answer from Phase 1:** The effect is **pair-dependent**. Two pairs gain on both classifiers, two lose on both, one is marginal (encoder), and one flips sign (70B). There is no general rule that cyber fine-tuning helps Scale-C-style MCQ evaluation [1], [2], [3], [4].

Topic-level detail—where gains and losses actually happen—is in Section 8. Classifier disagreement on the 70B pair is Section 9.

---

## References used in Chapter 7 (summary)

| Ref | Used for |
|-----|----------|
| [1] | Pairwise comparison as the right unit of analysis |
| [2] | Foundation-Sec domain pretraining |
| [3] | Instruction-tuned pairs (Lily, Baron, Trendyol) |
| [4] | Assistant-style tuning (ZySec); KL / forgetting context |
| [6] | CyBERTuned encoder pair |
| [7] | Model cards and training claims |
| [8] | MCQ accuracy and Δ definition |

---

## Author notes (remove from thesis)

- Re-run Llama 3.3 70B NLI to completion before citing +9.4 pp Trendyol delta in the conclusion.
- Harmonize 70B embedding item sets before treating −7.2 pp as final.
- Optional: add bootstrap confidence intervals on Δ if reviewers ask (not in current pipeline).
- In Word: place F8 after Table 7.1; use F8b only if page budget allows.
- Open Section 8 with one sentence linking largest topic-level swings to pairs named here (e.g. Lily on malware, ZySec on email).
