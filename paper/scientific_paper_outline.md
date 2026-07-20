# Scale_C: Scientific Paper Outline (Compact)

> **Purpose:** Page-limited paper skeleton — methodology + results + interpretation.  
> **Target length:** ~8–10 pages (conference) or ~12 pages (short journal).  
> **Rule:** Write prose only where marked; everything else is structure and guidance.

---

## Table of Contents

1. [Abstract](#1-abstract)
2. [Introduction](#2-introduction)
3. [Related Work](#3-related-work)
4. [Methodology](#4-methodology)
  - 4.1 [Design Goal](#41-design-goal)
  - 4.2 [Benchmark Structure](#42-benchmark-structure)
  - 4.3 [Dataset Construction](#43-dataset-construction)
  - 4.4 [Model Evaluation Protocol](#44-model-evaluation-protocol)
5. [Experimental Setup](#5-experimental-setup)
6. [Results](#6-results)
7. [Discussion — Why the Results Look Like This](#7-discussion--why-the-results-look-like-this)
8. [Limitations and Conclusion](#8-limitations-and-conclusion)
9. [References](#9-references)

---

## Page budget (suggested)


| Section                  | Pages    | Role                    |
| ------------------------ | -------- | ----------------------- |
| Abstract                 | 0.25     | Summary                 |
| Introduction             | 1.0      | Problem + contribution  |
| Related Work             | 0.75     | Positioning only        |
| **Methodology**          | **2.5**  | **Core of the paper**   |
| Experimental Setup       | 0.75     | Reproducibility         |
| Results                  | 1.5      | Evidence                |
| Discussion               | 1.25     | Interpretation          |
| Limitations + Conclusion | 0.5      | Honest close            |
| **Total**                | **~8.5** | + references / appendix |


---

## 1. Abstract

**Write (~150 words):**

- Problem: existing cyber LLM benchmarks mostly test MCQ knowledge, not deployable capability.
- Method: Scale_C — unify upstream benchmarks under one schema, classify by topic, curate a balanced corpus, evaluate base vs. domain-adapted models.
- Main result: *(fill in — e.g. domain FT improves MCQ modestly; capability gaps persist on hard sources / topics)*.
- Takeaway: answering questions well ≠ being ready for structured educational or safety-sensitive use.

---

## 2. Introduction

### What to establish

- **Gap:** CyberMetric, SecBench, MMLU-style tests measure *what the model knows*, not *what it can reliably do* in education workflows (H5P, MCQ generation) or under safety-relevant prompts.
- **Research question:** How do general and cybersecurity-adapted LLMs compare when evaluation is topic-balanced and spans knowledge *and* structured generation?
- **Hypothesis (optional):** Domain fine-tuning helps MCQ accuracy more on in-distribution cyber corpora than on reasoning-heavy or multilingual items; generation and safety may not improve in lockstep.

### Contributions (bullet list in paper)

1. A **reproducible pipeline**: raw benchmarks → unified schema → topic classification → curated eval set.
2. A **28-topic cybersecurity taxonomy** (`SCLC`*) for stratified analysis, not just aggregate accuracy.
3. **Empirical comparison** of paired base / fine-tuned models on the same corpus.
4. **Classification validation** via a 100-item frontier-labeled gold standard.

### Figure (1)

**Fig. 1 — Scale_C pipeline (one diagram):** sources → classify → curate → evaluate → interpret.

---

## 3. Related Work

*Keep short. Three paragraphs or subsections max.*


| Subsection               | Cover                                  | Skip                               |
| ------------------------ | -------------------------------------- | ---------------------------------- |
| Cyber LLM benchmarks     | CyberMetric, SecBench, cyberbench      | Long model descriptions            |
| General knowledge eval   | MMLU computer security subset          | Full MMLU survey                   |
| Generation / safety eval | H5P, schema benchmarks, safety rubrics | Tier 3 detail if not evaluated yet |


**Closing sentence:** Position Scale_C as *integration + stratification + paired comparison*, not another standalone MCQ set.

---

## 4. Methodology

*This is the main section. For each step: **what we did** → **why we did it that way**.*

### 4.1 Design Goal


| Choice               | What                                                              | Why                                                                |
| -------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------ |
| Unified schema       | Every item: `metadata`, `payload`, `evaluation`, `classification` | Same runner for heterogeneous upstream formats; comparable scoring |
| JSONL corpora        | One record per line                                               | Incremental builds, resume on failure, HF/Pandas friendly          |
| Topic stratification | 28 leaf labels (`schema/taxonomy.json`)                           | Aggregate accuracy hides weak domains; curation enforces balance   |
| Base vs. FT pairs    | e.g. Mistral ↔ Lily-Cyber, Llama ↔ Foundation-Sec                 | Isolates effect of domain adaptation on same architecture          |


### 4.2 Benchmark Structure

*Describe tiers briefly; report only what you actually evaluate in this paper.*


| Tier                                  | Measures                                                   | Status in paper         |
| ------------------------------------- | ---------------------------------------------------------- | ----------------------- |
| **Tier 1** — Factual cyber competence | MCQ answering, open explanation, mitigation, code analysis | **Primary**             |
| **Tier 2** — Structured generation    | MCQ/H5P generation, JSON validity                          | **If corpus has items** |
| **Tier 3** — Multilingual             | DE items, EN→DE                                            | **Optional / future**   |


**Metrics (Tier 1):** exact-match accuracy on letter answers; breakdown by `task_type`, upstream source, and `SCLC`* topic.

**Risk categories** (`safe`, `defensive`, `exploit_oriented`, …): mention only if safety items are in the evaluated corpus.

### 4.3 Dataset Construction

*Present as a numbered pipeline — readers should be able to replicate it.*

```
Raw sources  →  Normalize  →  Classify  →  Curate  →  Final corpus
```


| Step                   | Method                                                                                                       | Rationale                                                                          |
| ---------------------- | ------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| **1. Ingest**          | Pull from Hugging Face / GitHub (`fetch_datasets.py`); convert JSON/CSV/Parquet → JSONL                      | Reuse public benchmarks; avoid manual re-authoring                                 |
| **2. Normalize**       | Map rows to Scale_C schema (`schema/schema.json`)                                                            | Single evaluation harness (`eval_llm_benchmark.py`)                                |
| **3. Classify**        | Zero-shot topic assignment via NLI, embedding similarity, or generative classifier (`classify_zero_shot.py`) | Upstream datasets lack our taxonomy; automated labeling scales                     |
| **4. Curate**          | Top-*N* highest-confidence items per topic per benchmark (`build_final_dataset.py`; default *N*=10)          | Prevents large corpora (e.g. CyberMetric) from dominating; improves topic coverage |
| **5. Validate labels** | 100 MCQ gold set via frontier model + human-review CSV (`build_mcq_gold_standard.py`)                        | Quantify classifier trustworthiness before stratified claims                       |


**Two corpus variants:** `embedding`-classified vs. `nli`-classified — report both only if comparing classifiers; otherwise pick one as primary and mention the other in limitations.

**Fig. 2 (optional):** taxonomy cloud or bar chart of items per `SCLC`* topic after curation.

**Table 1:** Upstream sources, raw size, curated size, classifier used.

### 4.4 Model Evaluation Protocol


| Aspect          | Specification                                                      | Rationale                                        |
| --------------- | ------------------------------------------------------------------ | ------------------------------------------------ |
| Models          | Registry in `config/eval_models.json`; paired base + cyber FT      | Controlled comparison                            |
| Inference       | Hugging Face local and/or OpenRouter API (`eval_llm_benchmark.py`) | Same prompts across backends where possible      |
| Prompting       | MCQ completion with letter extraction                              | Standard, comparable to prior cyber benchmarks   |
| Scoring         | `evaluation.correct_answer` exact match                            | Objective, automatable                           |
| Aggregation     | Overall accuracy; slices by source, topic, task type               | Answers *where* models fail, not only *how much* |
| Reproducibility | Fixed corpus (`data/final_1/`), `--resume`, summary JSON per model | Auditable reruns                                 |


---

## 5. Experimental Setup

*Facts only — no interpretation here.*

### Corpus

- Primary eval set: `data/final_1/{embedding|nli}/` *(state which)*
- Curation: max 10 items per topic per benchmark
- Scorable items: *(from manifest / summary totals)*

### Models evaluated


| Pair             | Base                       | Fine-tuned           |
| ---------------- | -------------------------- | -------------------- |
| Mistral 7B       | `mistral-7b-instruct-v0.2` | `lily-cyber-7b`      |
| Zephyr 7B        | `zephyr-7b-beta`           | `zysec-7b`           |
| Llama 3.1 8B     | `llama-3.1-8b`             | `foundation-sec-8b`  |
| Qwen3 14B        | `qwen3-14b`                | `baronllm-v2`        |
| Llama 3.3 70B    | `llama-3.3-70b-instruct`   | `trendyol-cyber-70b` |
| Encoder baseline | `roberta-base`             | `cybertuned`         |


*List only models you actually ran for this paper.*

### Classification validation

- Gold standard: 100 MCQs (CyberMetric + MMLU computer_security)
- Metric: agreement between pipeline label and frontier label
- Report: overall % + disagreements on ambiguous topics

### Hardware / API

- GPUs, quantization, OpenRouter — one short paragraph for reproducibility.

---

## 6. Results

*Report numbers; save why for Section 7.*

### 6.1 Classification quality

- [ ] Gold-standard agreement (NLI vs. embedding vs. generative — if compared)
- [ ] Most confused topic pairs

### 6.2 Overall model accuracy

**Table 2 — Main results:** Model | Corpus | Accuracy | Δ vs. base

*Example structure from your runs (fill with final numbers):*


| Model                    | Scorable | Accuracy | Notes                      |
| ------------------------ | -------- | -------- | -------------------------- |
| llama-3.3-70b-instruct   | 1,353    | 75.7%    | strong on CyberMetric/MMLU |
| lily-cyber-7b            | 37,746   | 51.8%    | +5.9 pp vs. Mistral base   |
| mistral-7b-instruct-v0.2 | 37,746   | 45.9%    | base                       |


### 6.3 Stratified results (pick 2–3 slices max)

- **By upstream source** — which benchmarks separate models?
- **By topic (`SCLC`*)** — weakest topics for all models?
- **By task type** — MCQ vs. open explanation gap?

**Fig. 3:** Grouped bar chart — base vs. FT accuracy (overall or per pair).  
**Fig. 4 (optional):** Heatmap — topic × model accuracy.

### 6.4 Base vs. fine-tuned delta

- [ ] Per-pair improvement (absolute and relative)
- [ ] Cases where FT does *not* beat base (important negative result)

### 6.5 Tier 2 / generation (if included)

- [ ] JSON validity rate
- [ ] H5P compliance — only if enough items

*Do not pad with empty subsections — omit tiers you did not run.*

---

## 7. Discussion — Why the Results Look Like This

*This section answers "so what?" and "why?" — connect each result pattern to a cause.*

Use this template per finding:

> **Observation** → **Likely explanation** → **Implication**


| Observation (from §6)                                                    | Why it might be true                                                                           | Implication                                                          |
| ------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| FT models gain on cyber MCQ but less on MMLU / Global-MMLU               | Training data closer to CyberMetric distribution; less transfer to general or DE items         | Leaderboard rank depends on benchmark mix                            |
| High accuracy on CyberMetric, low on cybersoceval / threat-intel sources | Upstream difficulty and format differ; reasoning-heavy items need more than fact recall        | Single-source cyber scores are misleading                            |
| Open-explanation accuracy > MCQ or vice versa                            | Scoring leniency vs. strict letter match; or models better at fluent text than discrete choice | Task type must be reported separately                                |
| Modest FT delta despite "cyber" branding                                 | Continued pretrain / SFT size and objective may not cover full taxonomy                        | Domain label ≠ comprehensive competence                              |
| Classifier disagreements on specific topics                              | Semantically overlapping labels (e.g. email vs. social engineering)                            | Stratified analysis inherits label noise — gold standard bounds this |
| Encoder (CyBERTuned) vs. generative LLM                                  | Different task: choice ranking vs. generation                                                  | Not directly comparable — report separately                          |


### Core argument (1 paragraph)

*Draft the narrative you want reviewers to remember — e.g.:*

> Scale_C shows that cybersecurity LLM evaluation must be **stratified** and **multi-source**. Domain fine-tuning improves aggregate scores but does not uniformly lift hard reasoning corpora or all taxonomy topics. A model strong on CyberMetric-style MCQs can still fail on items that require applied reasoning or that fall outside training distribution.

### Practical recommendations (3 bullets max)

- For **benchmark designers:** require topic tags and multiple sources.
- For **model developers:** evaluate paired against base on the same curated corpus.
- For **educators / H5P workflows:** do not assume MCQ performance predicts generation quality.

---

## 8. Limitations and Conclusion

### Limitations (honest, short)

- Automated topic labels (mitigated by gold standard, not eliminated)
- MCQ-heavy current corpus; Tier 2/3 underrepresented if not evaluated
- API/quantization effects on some models
- Static snapshots of fast-moving cyber knowledge

### Conclusion (1 short paragraph)

- Restate problem, method, main empirical finding, and call for capability-based cyber LLM evaluation.

---

## 9. References

*Key citations to include:*

- CyberMetric, SecBench / cyberbench, MMLU
- SuperGLEBer (if DE items used)
- Zero-shot NLI classifier (mDeBERTa-xnli)
- Evaluated model cards (Lily-Cyber, Foundation-Sec, ZySec, BaronLLM, etc.)

---

## Appendix (only if venue allows extra pages)


| Item | Content                               |
| ---- | ------------------------------------- |
| A    | Full `SCLC`* taxonomy table           |
| B    | Gold-standard construction parameters |
| C    | Per-topic full results table          |
| D    | Prompt template for MCQ evaluation    |


---

## Checklist before submission

- [ ] Methodology §4 is self-contained (replicable without reading code)
- [ ] Every design choice in §4 has a "why" column answered
- [ ] Results §6 has no interpretation (only numbers and slices)
- [ ] Discussion §7 explicitly links each major table/figure to an explanation
- [ ] Page count fits venue limit (move taxonomy + full tables to appendix)
- [ ] Tiers / models not evaluated are omitted, not listed as empty sections