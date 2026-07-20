# Chapters 3–5 — Research objectives, dataset, model selection

Replace Sections 3–5 in `Scale-C_Final_Report.docx`.  
Citations **[1]–[11]** — see `report-references.md`.  
Tone matches `report-abstract-intro-draft.md` and `report-chapter2-draft.md`.

---

## 3. Research objectives and guiding questions

### 3.1 Primary objective

The goal of this benchmarking study is to find out which large language model Scale-C should use. Scale-C is an H5P-based computer security course; it needs a model that can eventually help with quiz content, explanations, structured H5P output, and possibly German material.

We are not asking which cyber model looks best on a leaderboard in isolation. We compare each fine-tuned candidate against its own base model under the same setup, so we can see whether the adaptation step actually helped [1], [7].

This report covers Phase 1 of that search: multiple-choice cybersecurity knowledge and reasoning (Scale-C Tier 1). H5P generation (Tier 2) and German localization (Tier 3) are part of the target evaluation plan but are not fully run yet. Any model ranking here is therefore incomplete for final Scale-C deployment.

### 3.2 Guiding questions

**RQ1 — Fine-tuning effect:** Does cybersecurity fine-tuning consistently improve performance, or does it depend on the model pair?

**RQ2 — Topic labeling:** When we assign items to Scale-C topics with NLI versus embedding classifiers [9], [10], do model rankings stay stable?

**RQ3 — Scale:** Do 70B models dominate, or can well-tuned 7B–8B models stay competitive on selected topics?

**RQ4 — Base quality:** When the base model is weak on our MCQ setup, how much can fine-tuning recover (Qwen3 → Baron)?

**RQ5 — H5P and structure (planned):** Can the leading Tier 1 models produce valid H5P JSON and usable didactic content? *Not evaluated in this report.*

**RQ6 — Safety and German (planned):** Do top candidates refuse harmful prompts and handle German content acceptably? *Not evaluated in this report.*

Phase 1 already gives partial answers to RQ1–RQ4. Fine-tuning helps some pairs and hurts others. Classifiers often agree but split on the 70B pair. Scale matters on some topics but not all. Baron improves a weak base without beating large models on every slice.

### 3.3 Figure

**[F2] Research design for Scale-C model selection**

Show: Scale-C teaching context → evaluation dataset → six base/fine-tuned pairs → Tier 1 MCQ scoring → topic breakdown (NLI vs embedding labels) → pairwise delta. Mark Tier 2/3 as future work.

---

## 4. Dataset construction and taxonomy

### 4.1 Purpose of the evaluation dataset

The evaluation dataset is not Scale-C course content. It is a pooled set of public benchmark items chosen because they overlap with topics Scale-C teaches. We use it to compare models before wiring one into the live platform.

An earlier pipeline snapshot processed about 1,777 records, of which 961 were scorable multiple-choice items. The latest run may differ; final counts should come from the current manifest in the repository once classification and evaluation are complete [11].

### 4.2 Benchmark sources

Table 4.1 lists the main sources. Framework names (MITRE ATT&CK, NIST CSF, NICE, OWASP ASVS, Bloom) describe how we think about coverage. They are not the automatic topic labels used in the pipeline.

**Table 4.1 — Benchmark sources and role in Scale-C evaluation**

| Source | Contribution to Scale-C evaluation | Typical item types in this study |
|--------|-----------------------------------|----------------------------------|
| MMLU computer security [8], [11] | Core security knowledge MCQ | Tier 1 MCQ |
| CyberBench [11] | Threat and knowledge reasoning | Tier 1 MCQ / scenarios |
| CyberMetric [11] | Expert-validated security knowledge | Tier 1 MCQ |
| CyberSOCEval [11] | SOC-style reasoning, malware analysis | Tier 1 MCQ |
| SEC-bench [11] | AppSec, CVE-related knowledge | Tier 1 MCQ |
| Global-MMLU [11] | Localized knowledge (incl. German) | Tier 1 MCQ; Tier 3 (planned) |
| JSONSchemaBench [11] | Structured JSON output | Tier 2 (planned) |
| superGLEBer [11] | German NLP tasks | Tier 3 proxy (planned) |

JSONSchemaBench and superGLEBer are in the pipeline for later tiers. Phase 1 results in this report are driven mainly by the cyber MCQ sources in the top half of the table.

### 4.3 Topic taxonomy

Items are mapped to Scale-C topics defined in `schema/taxonomy.json`. The taxonomy has **37 leaf labels** (e.g. Email, SSL certificates, Advanced malware types) grouped under **28 parent codes** (SCLC001–SCLC028). For course-level reporting, we use **eight curriculum groups** that bundle related leaves (Table 4.2).

Proposed metadata fields in the schema (risk, difficulty, cognitive skill) are not validated yet and are not used in the Phase 1 results.

**Table 4.2 — Eight course groups (curriculum-level rollup)**

| Course group | Example leaf topics |
|--------------|---------------------|
| Identity and access | Credential management, Authentication/Authorization, Unique logins, Encrypted vaults |
| Human factors and social engineering | Social engineering, Email, Psychological manipulation, Behavioral security |
| Malware and advanced threats | Viruses/Trojans, Adware, Advanced malware types, Advanced cyber threats |
| Network and secure communications | Firewalls, SSL certificates, Secure communication, Infrastructure protection |
| Safe computing and browsing | General hygiene, Safe browsing, USB safety, Header checks, Typos, Domains |
| Governance and organizational risk | Regulatory/Legal, Internal risks, Professional perspective |
| Application and distributed work | App security, Working from home, Remote/Traveling security |
| Foundations, defense, and resilience | Foundational concepts, General theory, Defensive measures, Backups & recovery, Other |

### 4.4 Topic classification (NLI and embeddings)

Each item is labeled with two independent zero-shot methods:

**NLI labeling.** The item text is scored against each candidate topic description as an entailment problem [9]. We use a multilingual NLI classifier (MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7 in the repository pipeline).

**Embedding labeling.** The item and each topic description are embedded; the closest label by cosine similarity wins [10].

These classifiers assign **topics to questions**, not scores to model answers. Running both methods gives two topic-labeled views of the same pool. If rankings change when we switch labeler, we treat that as a stability warning (see RQ2).

After labeling, the builder deduplicates items, keeps valid predictions, and caps how many items any single source can contribute per topic so one large dataset does not dominate [11].

### 4.5 Model scoring (Phase 1)

For multiple-choice items, each model answers the same prompt; we score with exact match against the gold letter:

accuracy = correct / scorable

Pairwise effect:

Δ = accuracy(fine-tuned) − accuracy(base)

Positive Δ means the fine-tuned model did better. This is the main Phase 1 metric because MCQ items have an unambiguous key [8].

Open responses, H5P generation, and German tasks need rubrics, schema validation, or human review. Those belong to Tier 2 and Tier 3 and are out of scope for the results chapters that follow.

### 4.6 Pipeline overview

Raw sources → normalize to JSONL → topic classification (NLI and embedding runs) → balanced evaluation set → model inference → MCQ accuracy and topic/course breakdown → pairwise deltas.

**[F4]** End-to-end pipeline diagram  
**[F5]** Dataset composition by source and course group  
**[F6]** Taxonomy: 37 leaves → 28 parent codes → 8 course groups; dashed box for unvalidated metadata (risk, difficulty, tier)

---

## 5. Model selection and evaluation design

### 5.1 Why pairwise comparison?

If we only ranked cyber models in a single table, we could not tell whether a high score came from fine-tuning, from a larger base, or from a different tokenizer and chat template. Pairing each adapted model with its closest base controls for that [1], [7].

The encoder pair (RoBERTa → CyBERTuned) is a special case: it scores by similarity ranking, not text generation [6]. It is a baseline, not a Scale-C deployment option.

### 5.2 Evaluated pairs

Table 5.1 lists the six pairs. All generative pairs share the same Phase 1 protocol (same items, same decoding settings per run, same MCQ extraction logic).

**Table 5.1 — Base and fine-tuned model pairs**

| Base model | Fine-tuned / domain model | Role in study |
|------------|---------------------------|---------------|
| RoBERTa base | CyBERTuned | Encoder baseline [6] |
| Llama 3.1 8B | Foundation-Sec-8B | Domain-pretrained LLM [2], [7] |
| Mistral-7B-Instruct-v0.2 | Lily-Cybersecurity-7B-v0.2 | Instruction-tuned cyber model [3], [7] |
| Zephyr-7B-Beta | ZySec-7B | Aligned cyber assistant [4], [7] |
| Qwen3 14B | BaronLLM v2 | Instruction-tuned cyber model on mid-size base [3], [7] |
| Llama 3.3 70B Instruct | Trendyol Cybersecurity LLM v2 70B | Large instruct + cyber SFT [3], [7] |

### 5.3 Why these pairs for Scale-C?

**Encoder pair.** Shows the gap between encoder similarity and generative answering. Useful context, not a product candidate.

**7B–8B pairs.** Realistic deployment size for a university project: modest GPU cost, local or hosted inference.

**Qwen3 / Baron.** Tests whether fine-tuning can rescue a base that underperforms on Phase 1 MCQ despite its size.

**70B pair.** Tests whether cyber SFT still adds value when the base is already strong, or whether it narrows behavior in ways that hurt some topics.

### 5.4 Practical constraints for Scale-C

Beyond accuracy, Scale-C will eventually need:

- valid H5P JSON (Tier 2);
- acceptable refusal behavior on exploit-style prompts;
- German or localized content where the course requires it;
- hardware and license constraints for hosting.

Phase 1 does not score these yet. Table 5.1 should be read as a shortlist for deeper Tier 2/3 testing, not as a final purchase decision.

Document per run: model revision, prompt template, temperature, max tokens, hardware, and repository commit (reproducibility table, Figure F18).

### 5.5 Figure

**[F3] Model-pair overview** — base vs fine-tuned, parameter count, adaptation type (from Table 2.1), Phase 1 status (complete / planned tiers).

---

## References used in Chapters 3–5 (summary)

| Ref | Used for |
|-----|----------|
| [1] | Pairwise fine-tuning comparison logic |
| [2] | Foundation-Sec-style domain pretraining |
| [3] | Instruction-tuned LLM pairs |
| [4] | Alignment-style assistant (ZySec) |
| [6] | CyBERTuned encoder pair |
| [7] | Named model pairs and training claims |
| [8] | MCQ benchmark evaluation (MMLU) |
| [9] | NLI zero-shot topic labeling |
| [10] | Embedding-based topic labeling |
| [11] | Benchmark corpora and pipeline manifests |

---

## Author notes (remove from thesis)

- Replace 1,777 / 961 with manifest counts after `classify_zero_shot.py` and model eval are finished.
- Confirm Table 4.2 course groups with Scale-C curriculum owners; adjust leaf-to-group mapping if needed.
- Add decoding parameters and GPU notes to Table 5.1 or F18 before submission.
- Phase 1 results in Chapters 6–11 remain provisional until reproduced from the repository.
