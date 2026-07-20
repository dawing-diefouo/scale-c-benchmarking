# Chapter 12 — Conclusion

Replace **Section 12** (or **Section 11** if you drop Limitations) in `Scale-C_Final_Report (1).docx`.  
Follows §10 Discussion. **Limitations omitted** per author choice—add a short paragraph in the conclusion if examiners require caveats.

---

## 12. Conclusion

Scale-C is an H5P-based computer security course that may eventually use a large language model to draft activities, explanations, and localized content. Before committing to a model, we ran a benchmarking study: six base/fine-tuned pairs, public cyber benchmarks mapped to our taxonomy, and Tier 1 multiple-choice evaluation under two topic-labeling views (NLI and embedding).

This report answers whether **cybersecurity fine-tuning** reliably beats a solid general base on that setup. The answer is **no—not in general**. It depends on the pair, the topic, and how items are labeled.

### What we found

**Fine-tuning helps some pairs and hurts others.** Mistral→Lily (+7 pp) and Qwen3→Baron (+14–17 pp) improve on both classifiers. Llama 3.1→Foundation-Sec and Zephyr→ZySec regress. Trendyol vs Llama 3.3 **splits by classifier** (+9.4 pp NLI, −7.2 pp embedding). A “cyber fine-tuned” label is not evidence of better benchmark performance.

**Absolute leaders are not the whole story.** Trendyol leads on NLI (65.1%); Llama 3.3 leads on embedding (75.7%, with denominator caveats). Lily and Llama 3.1 8B remain credible at 7B–8B scale for a university budget.

**Topic-level gaps matter for Scale-C.** Identity, network, and certificate-style MCQs are relatively strong across models. **Malware and advanced threats stay hard** even for 70B systems. No model is safe to trust blindly on those modules—human review stays in the loop.

**Two labelers are better than one.** Rankings mostly align (ρ ≈ 0.97), but the 70B fine-tuning verdict and the overall #1 model change with the classifier. Scale-C should not pick a winner from a single automatic pipeline.

### What we recommend for Scale-C (provisional)

Phase 1 was **MCQ only**. We did not test H5P JSON, didactic quality, German content, or safety. We therefore **do not name a final production model**—only a shortlist for the next evaluation phase.


| Priority                     | Model                        | Rationale                                                  |
| ---------------------------- | ---------------------------- | ---------------------------------------------------------- |
| **Test next (Tier 2)**       | **Lily-Cybersecurity-7B**    | Clearest fine-tuning win at deployable size.               |
| **Test next (Tier 2)**       | **Llama 3.1 8B (base)**      | Beats Foundation-Sec; strong on several hard topic slices. |
| **Pending same-item re-run** | **Llama 3.3 70B / Trendyol** | Highest MCQ scores; fine-tuning benefit unconfirmed.       |
| **Deprioritize**             | Foundation-Sec-8B, ZySec-7B  | Worse than their bases on Tier 1 MCQ.                      |


**BaronLLM v2** stays conditional: large gain over a weak Qwen3 base, but mid-pack overall—worth Tier 2 only if structured output looks good.

The honest closing line for Scale-C: **we narrowed the field on cybersecurity MCQ; Tier 2 H5P evaluation must decide the rest.**

### Contribution

For Scale-C, this study delivers a **reusable pipeline** (taxonomy, dataset builder, pairwise metrics, dual topic views) and an evidence-based shortlist—not a deployment decision.

More broadly, it shows that **single-number cyber LLM leaderboards can mislead**: pairwise comparison and topic breakdown expose where fine-tuning helps, where it hurts, and where the field still fails on hard threat content.

### Next steps

1. Run **Tier 2** (H5P / JSON schema, rubric-scored explanations).
2. Finish **70B re-evaluation** on a frozen, shared item set.
3. Add **safety** and **German (Tier 3)** checks where the course requires them.

When those are done, Scale-C can commit to a model—or a small split (e.g. 7B for drafting, larger for review)—with evidence that matches real platform use.Scale-C is an H5P-based computer security course that may eventually use a large language model to draft activities, explanations, and localized content. Before committing to a model, we ran a benchmarking study: six base/fine-tuned pairs, public cyber benchmarks mapped to our taxonomy, and Tier 1 multiple-choice evaluation under two topic-labeling views (NLI and embedding).

This report answers whether **cybersecurity fine-tuning** reliably beats a solid general base on that setup. The answer is **no—not in general**. It depends on the pair, the topic, and how items are labeled.

### What we found

**Fine-tuning helps some pairs and hurts others.** Mistral→Lily (+7 pp) and Qwen3→Baron (+14–17 pp) improve on both classifiers. Llama 3.1→Foundation-Sec and Zephyr→ZySec regress. Trendyol vs Llama 3.3 **splits by classifier** (+9.4 pp NLI, −7.2 pp embedding). A “cyber fine-tuned” label is not evidence of better benchmark performance.

**Absolute leaders are not the whole story.** Trendyol leads on NLI (65.1%); Llama 3.3 leads on embedding (75.7%, with denominator caveats). Lily and Llama 3.1 8B remain credible at 7B–8B scale for a university budget.

**Topic-level gaps matter for Scale-C.** Identity, network, and certificate-style MCQs are relatively strong across models. **Malware and advanced threats stay hard** even for 70B systems. No model is safe to trust blindly on those modules—human review stays in the loop.

**Two labelers are better than one.** Rankings mostly align (ρ ≈ 0.97), but the 70B fine-tuning verdict and the overall #1 model change with the classifier. Scale-C should not pick a winner from a single automatic pipeline.

### What we recommend for Scale-C (provisional)

Phase 1 was **MCQ only**. We did not test H5P JSON, didactic quality, German content, or safety. We therefore **do not name a final production model**—only a shortlist for the next evaluation phase.


| Priority                     | Model                        | Rationale                                                  |
| ---------------------------- | ---------------------------- | ---------------------------------------------------------- |
| **Test next (Tier 2)**       | **Lily-Cybersecurity-7B**    | Clearest fine-tuning win at deployable size.               |
| **Test next (Tier 2)**       | **Llama 3.1 8B (base)**      | Beats Foundation-Sec; strong on several hard topic slices. |
| **Pending same-item re-run** | **Llama 3.3 70B / Trendyol** | Highest MCQ scores; fine-tuning benefit unconfirmed.       |
| **Deprioritize**             | Foundation-Sec-8B, ZySec-7B  | Worse than their bases on Tier 1 MCQ.                      |


**BaronLLM v2** stays conditional: large gain over a weak Qwen3 base, but mid-pack overall—worth Tier 2 only if structured output looks good.

The honest closing line for Scale-C: **we narrowed the field on cybersecurity MCQ; Tier 2 H5P evaluation must decide the rest.**

### Contribution

For Scale-C, this study delivers a **reusable pipeline** (taxonomy, dataset builder, pairwise metrics, dual topic views) and an evidence-based shortlist—not a deployment decision.

More broadly, it shows that **single-number cyber LLM leaderboards can mislead**: pairwise comparison and topic breakdown expose where fine-tuning helps, where it hurts, and where the field still fails on hard threat content.

### Next steps

1. Run **Tier 2** (H5P / JSON schema, rubric-scored explanations).
2. Finish **70B re-evaluation** on a frozen, shared item set.
3. Add **safety** and **German (Tier 3)** checks where the course requires them.

When those are done, Scale-C can commit to a model—or a small split (e.g. 7B for drafting, larger for review)—with evidence that matches real platform use.Scale-C is an H5P-based computer security course that may eventually use a large language model to draft activities, explanations, and localized content. Before committing to a model, we ran a benchmarking study: six base/fine-tuned pairs, public cyber benchmarks mapped to our taxonomy, and Tier 1 multiple-choice evaluation under two topic-labeling views (NLI and embedding).

This report answers whether **cybersecurity fine-tuning** reliably beats a solid general base on that setup. The answer is **no—not in general**. It depends on the pair, the topic, and how items are labeled.

### What we found

**Fine-tuning helps some pairs and hurts others.** Mistral→Lily (+7 pp) and Qwen3→Baron (+14–17 pp) improve on both classifiers. Llama 3.1→Foundation-Sec and Zephyr→ZySec regress. Trendyol vs Llama 3.3 **splits by classifier** (+9.4 pp NLI, −7.2 pp embedding). A “cyber fine-tuned” label is not evidence of better benchmark performance.

**Absolute leaders are not the whole story.** Trendyol leads on NLI (65.1%); Llama 3.3 leads on embedding (75.7%, with denominator caveats). Lily and Llama 3.1 8B remain credible at 7B–8B scale for a university budget.

**Topic-level gaps matter for Scale-C.** Identity, network, and certificate-style MCQs are relatively strong across models. **Malware and advanced threats stay hard** even for 70B systems. No model is safe to trust blindly on those modules—human review stays in the loop.

**Two labelers are better than one.** Rankings mostly align (ρ ≈ 0.97), but the 70B fine-tuning verdict and the overall #1 model change with the classifier. Scale-C should not pick a winner from a single automatic pipeline.

### What we recommend for Scale-C (provisional)

Phase 1 was **MCQ only**. We did not test H5P JSON, didactic quality, German content, or safety. We therefore **do not name a final production model**—only a shortlist for the next evaluation phase.


| Priority                     | Model                        | Rationale                                                  |
| ---------------------------- | ---------------------------- | ---------------------------------------------------------- |
| **Test next (Tier 2)**       | **Lily-Cybersecurity-7B**    | Clearest fine-tuning win at deployable size.               |
| **Test next (Tier 2)**       | **Llama 3.1 8B (base)**      | Beats Foundation-Sec; strong on several hard topic slices. |
| **Pending same-item re-run** | **Llama 3.3 70B / Trendyol** | Highest MCQ scores; fine-tuning benefit unconfirmed.       |
| **Deprioritize**             | Foundation-Sec-8B, ZySec-7B  | Worse than their bases on Tier 1 MCQ.                      |


**BaronLLM v2** stays conditional: large gain over a weak Qwen3 base, but mid-pack overall—worth Tier 2 only if structured output looks good.

The honest closing line for Scale-C: **we narrowed the field on cybersecurity MCQ; Tier 2 H5P evaluation must decide the rest.**

### Contribution

For Scale-C, this study delivers a **reusable pipeline** (taxonomy, dataset builder, pairwise metrics, dual topic views) and an evidence-based shortlist—not a deployment decision.

More broadly, it shows that **single-number cyber LLM leaderboards can mislead**: pairwise comparison and topic breakdown expose where fine-tuning helps, where it hurts, and where the field still fails on hard threat content.

### Next steps

1. Run **Tier 2** (H5P / JSON schema, rubric-scored explanations).
2. Finish **70B re-evaluation** on a frozen, shared item set.
3. Add **safety** and **German (Tier 3)** checks where the course requires them.

When those are done, Scale-C can commit to a model—or a small split (e.g. 7B for drafting, larger for review)—with evidence that matches real platform use.

---



## Author notes (remove from thesis)

- If examiners require limitations, paste §11 from `report-chapter11-12-draft.md` or add one paragraph here on Tier 1 scope and partial 70B NLI run.  
- Align section number with your Word outline (11 vs 12 if Limitations is removed).

