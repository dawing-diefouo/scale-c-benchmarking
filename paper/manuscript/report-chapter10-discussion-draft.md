# Chapter 10 — Discussion (replaces old Sections 10–12)

Replace **Sections 10, 11, and 12** in `Scale-C_Final_Report (1).docx` with **this single chapter**.  
Renumber what follows: **Limitations → 11**, **Conclusion → 12**.

---

## What to skip and why

| Old section | Verdict | Reason |
|-------------|---------|--------|
| **10 — Reasoning architecture vs scale** | **Skip** | Already covered in §7 (Qwen3→Baron), §8 Table 8.2, and RQ4 notes. A separate chapter would repeat tables and breaks the pairwise design by comparing unrelated model sizes. |
| **11 — Hardest benchmark areas** | **Skip** | Already covered in §8.1–8.2 (malware/threats, course averages, F10/F16). Qualitative error analysis (old F17) is still **future work**—mention under Limitations, not a results chapter. |
| **12 — Discussion** | **Keep → becomes §10** | Required for the thesis: synthesis, Scale-C implications, answers to RQs. |

No new figures are required here; refer back to F7–F13 as needed.

---

## 10. Discussion: what Phase 1 means for Scale-C

This benchmarking study exists to help **choose a language model for Scale-C**—an H5P-based computer security course—not to settle a general leaderboard for “cyber LLMs.” Phase 1 tested **Tier 1 multiple-choice** knowledge and reasoning only. We have not yet run H5P JSON generation (Tier 2), German localization (Tier 3), or systematic safety checks. Everything below is **provisional** until those tiers are evaluated.

### 10.1 Answers to the research questions

**RQ1 — Does cyber fine-tuning consistently help?**  
**No.** It depends on the pair. Lily (+7 pp) and Baron (+14–17 pp) improve on both classifier views. Foundation-Sec (−6 to −9 pp) and ZySec (−7 to −11 pp) get worse. Trendyol is inconclusive (+9.4 pp NLI, −7.2 pp embedding). The label on the model card is not a useful predictor [1], [7].

**RQ2 — Do rankings stay stable when we change the topic labeler?**  
**Mostly, but not where it counts.** Global rank order correlates strongly (ρ ≈ 0.97), yet the overall leader flips (Trendyol under NLI, Llama 3.3 under embedding), and the 70B fine-tuning verdict reverses. Scale-C should not rely on a single automatic topic pipeline [9], [10].

**RQ3 — Do 70B models dominate?**  
**On many slices, yes—but not universally.** Llama 3.3 and Trendyol lead on identity, network, and absolute MCQ scores. Well-tuned 7B models (especially Lily, and Llama 3.1 8B base) stay in range for a resource-limited university deployment. Scale buys capacity on hard theory/threat topics; it does not fix every course group (malware stays ~42–58% even for large models).

**RQ4 — Can fine-tuning rescue a weak base?**  
**Partially.** Baron roughly doubles Qwen3’s score but remains mid-pack overall. Fine-tuning fixed a badly matched base more than it produced a new leader. For Scale-C, that means: fix serving/prompting first, then judge whether cyber SFT is worth the cost.

### 10.2 Five findings that hold up (compressed)

1. **Pairwise comparison is the right unit of analysis.** Global tables mix winners and losers; only base-vs-fine-tuned Δ isolates the effect of adaptation (§7).

2. **Generative LLMs are the relevant class for Scale-C.** Encoder fine-tuning (RoBERTa→CyBERTuned) adds ~0.5 pp; the jump to a 7B generative model adds ~37 pp (§6). H5P authoring needs generation, not choice ranking.

3. **Topic-level detail matters.** Lily gains on malware but can slip on email; Trendyol gains on some NLI slices but loses on social engineering under embedding (§8). No model is “good at cybersecurity” without naming the topic and classifier.

4. **Malware and advanced threats expose a real gap.** Every model struggles there relative to identity/network content (§8). Scale-C should plan **human review** for those modules regardless of which LLM we adopt.

5. **Multi-view evaluation is justified.** If one classifier were enough, NLI and embedding would tell the same story. They do not—especially for the 70B pair (§9).

### 10.3 Implications for Scale-C model selection (Phase 1 only)

This is not a final deployment decision. It is a **shortlist and avoid list** for Tier 2/3 testing.

**Continue evaluating (Tier 2 priority)**

| Candidate | Why |
|-----------|-----|
| **Lily-Cybersecurity-7B** | Clearest 7B fine-tuning win; reasonable absolute MCQ; plausible GPU budget for a university project. |
| **Llama 3.1 8B (base)** | Beats Foundation-Sec on Tier 1; strong on theory/threat slices vs Qwen3/Baron; general instruct model may transfer better to open-ended H5P tasks. |
| **Llama 3.3 70B / Trendyol** | Highest absolute Tier 1 scores, but **only after** same-item re-run and hosting-cost review. Trendyol is not confirmed as an upgrade over the base. |

**Deprioritize for Tier 1 MCQ (avoid unless Tier 2 surprises)**

| Model | Why |
|-------|-----|
| **Foundation-Sec-8B** | Consistent regression vs Llama 3.1 base. |
| **ZySec-7B** | Largest consistent loss; topic-level damage on email, foundations, regulatory content. |
| **Encoder-only paths (CyBERTuned)** | Control only; not suitable for H5P or explanations. |

**Conditional**

| Model | Why |
|-------|-----|
| **BaronLLM v2** | Large Δ over Qwen3 but weak absolute scores; worth Tier 2 only if Qwen3 base was misconfigured and Baron shows H5P/schema strength. |
| **Qwen3 14B base** | Poor Phase 1 MCQ; investigate prompt/backend before ruling out. |

**What we still cannot rank**

- Valid **H5P JSON** and didactic quality (Tier 2)—primary Scale-C use case.  
- **German** content (Tier 3).  
- **Refusal behavior** on harmful or exploit-style prompts.  
- **Qualitative failure modes** on malware/threat items (planned error analysis, not done).

Until Tier 2 runs, the honest statement for the thesis is: **we narrowed the field on cyber MCQ; we have not yet chosen Scale-C’s model.**

### 10.4 Methodological contribution (for the report, not the product)

This study’s value for the literature is modest but clear: a **pairwise, multi-source, topic-labeled** benchmark tied to a real curriculum taxonomy, scored under two independent topic views. It shows that cyber fine-tuning evaluations that only publish a single accuracy number can mislead—both about which model wins and about whether fine-tuning helped.

For Scale-C specifically, the methodological lesson is practical: **run the same evaluation protocol you care about in production** (MCQ + structured JSON + locale + safety), on items that match your course topics, with frozen manifests and reported n/N.

### 10.5 What we would do next (feeds Section 12 Conclusion)

Ordered by importance for Scale-C:

1. **Tier 2 — H5P / JSONSchemaBench:** schema-valid output, distractor quality, rubric-scored explanations.  
2. **Same-item re-evaluation** of Llama 3.3 vs Trendyol (complete NLI, harmonize embedding n).  
3. **Safety spot-checks** on misuse-style prompts.  
4. **Tier 3 — German / Global-MMLU** where the course requires localization.  
5. **Qualitative error analysis** on malware/threat failures (old Section 11 content, as appendix material).

---

## Author notes (remove from thesis)

- After inserting this chapter, delete old §10–§12 headings from the Word doc to avoid duplication.  
- Section **11 Limitations** and **12 Conclusion** still need separate drafts (not covered here).  
- If examiners require a “hardest topics” section, point them to §8.2 + Figure F16—do not restore old §11.
