# Chapter 6 — Phase 1 overall accuracy (Tier 1 MCQ)

Replace **Section 6** in `Scale-C_Final_Report (1).docx`.  
Citations **[1]**, **[7]**, **[8]**, **[11]** — see `report-references.md`.  
Tone matches `report-abstract-intro-draft.md` and `report-chapter3-5-draft.md`.

**Proposed section title (replaces “Global Results”):**

> **6. Phase 1 overall accuracy: Tier 1 MCQ leaderboard**

This name ties the chapter to Scale-C’s evaluation tiers and to the concrete metric used in Phase 1 (multiple-choice accuracy), rather than a generic “global results” label.

---

## 6. Phase 1 overall accuracy: Tier 1 MCQ leaderboard

This chapter answers a narrow but necessary question for Scale-C model selection: **on our pooled Tier 1 benchmark, which candidates score highest on multiple-choice cybersecurity knowledge and reasoning?**

Phase 1 does **not** decide the final Scale-C model. H5P generation (Tier 2) and German localization (Tier 3) are still outstanding. What we get here is a **provisional shortlist signal**: which models are strong enough on cyber MCQ to justify deeper testing, and which “cyber fine-tuned” labels are misleading at the aggregate level.

All numbers below come from the repository run stored in `data/eval_1/` (evaluation corpus `data/final_1`, classifier-specific JSONL inputs). They supersede presentation-only slides unless a re-run changes the manifest.

### 6.1 What we measure

For each model and classifier view, we report:

accuracy = correct answers / scorable items

as defined in Section 4.5 [8]. Items are the same benchmark pool described in Chapter 4; only the **topic labels** differ between the NLI and embedding classifier runs [9], [10]. That means NLI and embedding columns are **two reporting views**, not two scores on an identical frozen item set. We do not declare a single “winner” by mixing them.

**NLI-classified corpus:** 573 scorable items per generative model (encoder pair included).  
**Embedding-classified corpus:** 847 scorable items per generative model, except Llama 3.3 70B (see below).

### 6.2 Overall leaderboard

Table 6.1 lists all twelve evaluated systems (six base/fine-tuned pairs from Table 5.1). Fine-tuned rows are marked; bases are the comparison anchors for Section 7.

**Table 6.1 — Phase 1 overall MCQ accuracy (**`data/eval_1`**)**


| Model                             | Role                   | NLI acc. (n/N)      | Embedding acc. (n/N) |
| --------------------------------- | ---------------------- | ------------------- | -------------------- |
| RoBERTa base                      | Encoder baseline [6]   | 21.1% (121/573)     | 26.7% (226/847)      |
| CyBERTuned                        | Encoder fine-tuned [6] | 21.6% (124/573)     | 27.0% (229/847)      |
| Llama 3.1 8B                      | Base                   | 57.9% (332/573)     | 60.9% (516/847)      |
| Foundation-Sec-8B                 | Fine-tuned [2], [7]    | 52.2% (299/573)     | 52.2% (442/847)      |
| Mistral-7B-Instruct-v0.2          | Base                   | 44.5% (255/573)     | 46.9% (397/847)      |
| Lily-Cybersecurity-7B             | Fine-tuned [3], [7]    | 51.5% (295/573)     | 53.7% (455/847)      |
| Zephyr-7B-Beta                    | Base                   | 37.9% (217/573)     | 43.2% (366/847)      |
| ZySec-7B                          | Fine-tuned [4], [7]    | 27.1% (155/573)     | 36.0% (305/847)      |
| Qwen3 14B                         | Base                   | 11.9% (68/573)      | 13.9% (118/847)      |
| BaronLLM v2                       | Fine-tuned [3], [7]    | 26.2% (149/569)     | 30.8% (258/837)      |
| Llama 3.3 70B Instruct            | Base                   | 55.7% (182/327) †   | 75.7% (1024/1353) ‡  |
| Trendyol Cybersecurity LLM v2 70B | Fine-tuned [3], [7]    | **65.1% (373/573)** | 68.5% (580/847)      |


† **Partial NLI run:** Llama 3.3 70B base was evaluated on 327 of 573 NLI items when these summaries were generated. Treat NLI rankings that depend on this model as provisional until the run completes.  
‡ **Larger embedding denominator:** Llama 3.3 70B embedding evaluation includes 1,353 scorable items (additional task types beyond strict MCQ in the same corpus). Other models use 847. Do not rank Llama 3.3 embedding accuracy directly against 847-item models without harmonizing the item set.

**Reading the table for Scale-C**

- **Within NLI (573 items):** Trendyol 70B leads at 65.1%. Among fully evaluated generative models, Llama 3.1 8B (57.9%) and Lily (51.5%) follow. Qwen3 14B is weakest at 11.9%.
- **Within embedding (847 items, comparable n):** Trendyol 70B leads at 68.5%, then Lily (53.7%) and Foundation-Sec (52.2%). Qwen3 14B remains lowest at 13.9%.
- **Across classifiers:** There is no single global leader. NLI and embedding can reorder models because topic assignment and item counts differ [9], [10]. Section 9 discusses this explicitly for the 70B pair.

A high absolute score here supports **continued evaluation** (Tier 2/3, safety checks, hosting cost). It is not, by itself, a deployment recommendation for Scale-C.

### 6.3 Figures

**[F7] Phase 1 overall accuracy — NLI vs embedding (all candidates)**

Figure F7 — Global accuracy by classifier

*Caption:* Grouped bars for all twelve systems under NLI (blue) and embedding (magenta) topic labeling. Annotations show rounded percentages. Dashed line marks the encoder ceiling (~21% NLI). Footnote: Llama 3.3 70B NLI is partial (327/573); embedding n varies (see Table 6.1). Source: `data/eval_1/*/ *_summary.json`, figure `figures/eval_1/analysis/01_global_nli_vs_embedding.png`.

**[F9] Encoder vs generative answering gap**

Figure F9 — Encoder vs generative gap



### 6.4 Encoder ceiling vs generative LLMs

The encoder pair (RoBERTa → CyBERTuned) scores **21–27%** regardless of classifier [6]. CyBERTuned improves marginally over RoBERTa (+0.5 pp NLI, +0.3 pp embedding). That is expected: both models answer by ranking choices with embeddings, not by generating a letter.

The step to a **7B generative instruct model** (Llama 3.1 8B) adds roughly **37 pp** under NLI and **34 pp** under embedding. This gap dominates any gain from cybersecurity encoder fine-tuning. For Scale-C’s planned use cases—drafting quiz text, producing structured H5P, explaining concepts to learners—the practical implication is clear: **generative instruction-tuned LLMs are the relevant candidate class**; encoder pairs belong in the report as a scientific control, not as platform options.

### 6.5 What overall accuracy does and does not tell Scale-C

**What it tells us**

1. **Cyber branding is not enough.** Several fine-tuned models score below their bases on aggregate accuracy (Foundation-Sec, ZySec; details in Section 7). A “cybersecurity LLM” label does not guarantee better Tier 1 MCQ performance [1], [7].
2. **Scale helps but is not the whole story.** 70B models top the leaderboard on both views (with the denominator caveats above), yet 7B–8B models such as Llama 3.1 8B and Lily remain competitive in absolute terms—useful for a university project with modest GPU budget.
3. **Weak bases can be partially rescued.** Qwen3 14B scores 11.9–13.9% globally; BaronLLM v2 roughly doubles that (Section 7). That pattern matters if Scale-C considers mid-size models for cost reasons.
4. **Malware and advanced threats stay hard everywhere.** Even the best overall models leave substantial headroom on the hardest course groups (Section 8). Scale-C content pipelines should not assume the model will reliably handle those topics without human review.

**What it does not tell us**

- Valid **H5P JSON** or didactic quality (Tier 2).
- **German** or multilingual behavior (Tier 3).
- **Safety** refusals on exploit-style prompts.
- **Pairwise fine-tuning effects** (Section 7) or **topic-level** strengths (Section 8).

Until those tiers are run, Table 6.1 should be read as **Phase 1 screening**, not a final Scale-C model choice.

### 6.6 Link to research questions


| RQ                         | Phase 1 overall picture (this chapter)                                                                            |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| RQ1 — Fine-tuning effect   | Aggregate accuracy alone mixes winners and losers; pair-level Δ in Section 7 is the cleaner test.                 |
| RQ2 — Classifier stability | Different leaders and orderings under NLI vs embedding; no single leaderboard.                                    |
| RQ3 — Scale                | 70B models lead on both views (with n caveats); 7B–8B models remain in range for resource-constrained deployment. |
| RQ4 — Weak base recovery   | Qwen3 is lowest globally; Baron improves but stays mid-pack in absolute terms.                                    |




### 6.7 Reproducibility note

Document for the thesis appendix (full table: Figure F18 in Section 13):


| Field             | Phase 1 value                                                                                                          |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Evaluation corpus | `data/final_1` (classifier-specific builds)                                                                            |
| Results path      | `data/eval_1/{nli,embedding}/`                                                                                         |
| Metric            | MCQ exact-match accuracy                                                                                               |
| Classifiers       | NLI: `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7`; embedding: sentence-transformers per pipeline config |
| Figures           | `figures/eval_1/analysis/01_global_nli_vs_embedding.png`, `09_encoder_vs_generative.png`                               |
| Known gaps        | Llama 3.3 70B NLI partial; embedding n mismatch for Llama 3.3                                                          |


---



## References used in Chapter 6 (summary)


| Ref  | Used for                                                       |
| ---- | -------------------------------------------------------------- |
| [1]  | Why pairwise comparison matters more than raw leaderboard rank |
| [2]  | Foundation-Sec continued pretraining context                   |
| [3]  | Instruction-tuned cyber LLMs (Lily, Baron, Trendyol)           |
| [4]  | Assistant-style tuning (ZySec)                                 |
| [6]  | CyBERTuned encoder baseline and scoring method                 |
| [7]  | Model documentation and training claims                        |
| [8]  | MCQ accuracy as primary Phase 1 metric                         |
| [9]  | NLI topic-labeling view                                        |
| [10] | Embedding topic-labeling view                                  |
| [11] | Benchmark corpora and `data/eval_1` manifests                  |


---



## Author notes (remove from thesis)

- Re-run `llama-3.3-70b-instruct` on the full NLI corpus (573 items) and refresh Table 6.1 / F7 before submission.
- Harmonize Llama 3.3 embedding evaluation to the same 847-item MCQ subset as other models, or split Table 6.1 into “strict MCQ” and “extended corpus” rows.
- Insert F7 and F9 into the Word document at 100% width; use the caption text above.
- Section 7 should open with “Building on Table 6.1…” to avoid repeating the full leaderboard.

