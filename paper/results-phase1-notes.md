# Phase 1 interpretation notes

> Scope: frozen Phase 1 corpora under ``data/phase1/`` and summaries in
> ``data/results/phase1/``. Scorable denominators: **573** (NLI) / **847** (embedding).
>
> Older notes referring to ``data/final_1`` or ``data/eval_1`` describe the same
> experiment before the repository cleanup.

## Model families (base → fine-tuned)

Each row is one comparison family from `config/eval_models.json`. The **base** is the upstream model; the **fine-tuned** model is the cyber-specialized (or encoder-tuned) derivative.

| # | Base model | Fine-tuned model | Backend |
| --- | --- | --- | --- |
| 1 | Llama 3.1 8B (base) | Foundation-Sec-8B | huggingface |
| 2 | Mistral 7B Instruct v0.2 (base) | Lily Cyber. 7B v0.2 | huggingface |
| 3 | Zephyr 7B Beta (base) | ZySec-7B | huggingface |
| 4 | Qwen3 14B (base) | BaronLLM v2.0 | openai |
| 5 | Llama 3.3 70B Instruct (base) | Trendyol Cyber. LLM v2 (70B) | openai |
| 6 | RoBERTa Base (base) | CyBERTuned | choice_ranking |

## Evaluation coverage on `data/final_1`

Before comparing base vs fine-tuned, both sides must be evaluated on the **same** `data/final_1` pool. Scorables differ between `embedding` and `nli` classifier corpora even for the same model.

![Coverage matrix](../figures/eval_1/01_coverage_matrix.png)
![All pairs overview](../figures/eval_1/02_pairs_overview.png)

| Pair | Corpus | Base on final_1 | Fine-tuned on final_1 |
| --- | --- | --- | --- |
| Llama 3.1 8B (base) → Foundation-Sec-8B | embedding | **no** | **no** |
| Llama 3.1 8B (base) → Foundation-Sec-8B | nli | **no** | **no** |
| Mistral 7B Instruct v0.2 (base) → Lily Cyber. 7B v0.2 | embedding | **no** | **no** |
| Mistral 7B Instruct v0.2 (base) → Lily Cyber. 7B v0.2 | nli | **no** | **no** |
| Zephyr 7B Beta (base) → ZySec-7B | embedding | **no** | **no** |
| Zephyr 7B Beta (base) → ZySec-7B | nli | **no** | **no** |
| Qwen3 14B (base) → BaronLLM v2.0 | embedding | yes | **no** |
| Qwen3 14B (base) → BaronLLM v2.0 | nli | yes | **no** |
| Llama 3.3 70B Instruct (base) → Trendyol Cyber. LLM v2 (70B) | embedding | yes | **no** |
| Llama 3.3 70B Instruct (base) → Trendyol Cyber. LLM v2 (70B) | nli | yes | **no** |
| RoBERTa Base (base) → CyBERTuned | embedding | **no** | **no** |
| RoBERTa Base (base) → CyBERTuned | nli | **no** | **no** |

## Currently evaluated on `data/final_1`

Only **two base models** have `final_1` runs so far; **no fine-tuned model** has been evaluated on `final_1` yet.

![Evaluated bases](../figures/eval_1/03_evaluated_bases.png)
![Base models: embedding vs nli](../figures/eval_1/04_embedding_vs_nli_bases.png)

| Base model | Paired fine-tuned | Corpus | Scorable | Accuracy | Run notes |
| --- | --- | --- | ---: | --- | --- |
| Qwen3 14B (base) | fine-tuned → BaronLLM v2.0 | embedding | 1282 | 81.7% | OpenRouter API — authoritative Qwen3-14B base on data/final_1. |
| Qwen3 14B (base) | fine-tuned → BaronLLM v2.0 | nli | 315 | 61.3% | OpenRouter API — authoritative Qwen3-14B base on data/final_1. |
| Llama 3.3 70B Instruct (base) | fine-tuned → Trendyol Cyber. LLM v2 (70B) | embedding | 1353 | 75.7% | eval_1 |
| Llama 3.3 70B Instruct (base) | fine-tuned → Trendyol Cyber. LLM v2 (70B) | nli | 327 | 55.7% | eval_1 |

> **Partial run:** `llama-3.3-70b-instruct` NLI stopped at **327** scorable items (55.7%). Re-run to completion before NLI conclusions.

---

# Pair-by-pair breakdown

## Llama 3.1 8B (base) → Foundation-Sec-8B

- **Base model:** `llama-3.1-8b` — Llama 3.1 8B (base)
- **Fine-tuned model:** `foundation-sec-8b` — Foundation-Sec-8B
- **Backend:** `huggingface`

### Evaluation status on `data/final_1`

| Classifier corpus | Base evaluated? | Fine-tuned evaluated? |
| --- | --- | --- |
| embedding | **pending** | **pending** |
| nli | **pending** | **pending** |

*Neither side of this pair has been evaluated on `data/final_1` yet. Run both `llama-3.1-8b` and `foundation-sec-8b` on `data/final_1/{embedding,nli}` before drawing pair conclusions.*

---

## Mistral 7B Instruct v0.2 (base) → Lily Cyber. 7B v0.2

- **Base model:** `mistral-7b-instruct-v0.2` — Mistral 7B Instruct v0.2 (base)
- **Fine-tuned model:** `lily-cyber-7b` — Lily Cyber. 7B v0.2
- **Backend:** `huggingface`

### Evaluation status on `data/final_1`

| Classifier corpus | Base evaluated? | Fine-tuned evaluated? |
| --- | --- | --- |
| embedding | **pending** | **pending** |
| nli | **pending** | **pending** |

*Neither side of this pair has been evaluated on `data/final_1` yet. Run both `mistral-7b-instruct-v0.2` and `lily-cyber-7b` on `data/final_1/{embedding,nli}` before drawing pair conclusions.*

---

## Zephyr 7B Beta (base) → ZySec-7B

- **Base model:** `zephyr-7b-beta` — Zephyr 7B Beta (base)
- **Fine-tuned model:** `zysec-7b` — ZySec-7B
- **Backend:** `huggingface`

### Evaluation status on `data/final_1`

| Classifier corpus | Base evaluated? | Fine-tuned evaluated? |
| --- | --- | --- |
| embedding | **pending** | **pending** |
| nli | **pending** | **pending** |

*Neither side of this pair has been evaluated on `data/final_1` yet. Run both `zephyr-7b-beta` and `zysec-7b` on `data/final_1/{embedding,nli}` before drawing pair conclusions.*

---

## Qwen3 14B (base) → BaronLLM v2.0

- **Base model:** `qwen3-14b` — Qwen3 14B (base)
- **Fine-tuned model:** `baronllm-v2` — BaronLLM v2.0
- **Backend:** `openai`

### Evaluation status on `data/final_1`

| Classifier corpus | Base evaluated? | Fine-tuned evaluated? |
| --- | --- | --- |
| embedding | yes — 81.7%, n=1282 (eval_1_openrouter) | **pending** |
| nli | yes — 61.3%, n=315 (eval_1_openrouter) | **pending** |

### Overall accuracy

| Corpus | Qwen3 14B (base) | BaronLLM v2.0 | Δ |
| --- | --- | --- | ---: |
| embedding | 81.7% (n=1282) | *(not evaluated on final_1)* | — |
| nli | 61.3% (n=315) | *(not evaluated on final_1)* | — |

### By task type

**embedding**

| Task type | Base | Fine-tuned | Δ |
| --- | --- | --- | ---: |
| code_configuration_analysis | 100.0% (n=4) | *(not evaluated on final_1)* | — |
| german_h5p_generation | 100.0% (n=1) | *(not evaluated on final_1)* | — |
| h5p_mcq_generation | 100.0% (n=6) | *(not evaluated on final_1)* | — |
| h5p_structured_generation | 50.0% (n=2) | *(not evaluated on final_1)* | — |
| mcq_answering | 75.4% (n=781) | *(not evaluated on final_1)* | — |
| mcq_generation | 100.0% (n=1) | *(not evaluated on final_1)* | — |
| mitigation_defense_strategy | 91.1% (n=45) | *(not evaluated on final_1)* | — |
| open_explanation | 91.4% (n=442) | *(not evaluated on final_1)* | — |

**nli**

| Task type | Base | Fine-tuned | Δ |
| --- | --- | --- | ---: |
| code_configuration_analysis | — (no items) | *(not evaluated on final_1)* | — |
| german_h5p_generation | — (no items) | *(not evaluated on final_1)* | — |
| h5p_mcq_generation | — (no items) | *(not evaluated on final_1)* | — |
| h5p_structured_generation | — (no items) | *(not evaluated on final_1)* | — |
| mcq_answering | 61.3% (n=315) | *(not evaluated on final_1)* | — |
| mcq_generation | — (no items) | *(not evaluated on final_1)* | — |
| mitigation_defense_strategy | — (no items) | *(not evaluated on final_1)* | — |
| open_explanation | — (no items) | *(not evaluated on final_1)* | — |

### By upstream source

**embedding**

| Source | Base | Fine-tuned | Δ |
| --- | --- | --- | ---: |
| CyberMetric | 89.5% (n=295) | *(not evaluated on final_1)* | — |
| CyberMetric-10000-v1 | 95.2% (n=146) | *(not evaluated on final_1)* | — |
| Global-MMLU DE | 79.4% (n=199) | *(not evaluated on final_1)* | — |
| Global-MMLU EN | 94.5% (n=109) | *(not evaluated on final_1)* | — |
| MMLU college CS | 94.7% (n=38) | *(not evaluated on final_1)* | — |
| MMLU comp. sec. | 91.1% (n=168) | *(not evaluated on final_1)* | — |
| cybersoceval | 32.8% (n=119) | *(not evaluated on final_1)* | — |
| dev-00000-of-00001 | 0.0% (n=2) | *(not evaluated on final_1)* | — |
| malware_analysis-00000-of- | 27.8% (n=18) | *(not evaluated on final_1)* | — |
| test | 100.0% (n=17) | *(not evaluated on final_1)* | — |
| test-00000-of-00001 | 86.7% (n=135) | *(not evaluated on final_1)* | — |
| threat_intel_reasoning-000 | 41.2% (n=34) | *(not evaluated on final_1)* | — |
| validation | 100.0% (n=2) | *(not evaluated on final_1)* | — |

**nli**

| Source | Base | Fine-tuned | Δ |
| --- | --- | --- | ---: |
| CyberMetric | — (no items) | *(not evaluated on final_1)* | — |
| CyberMetric-10000-v1 | — (no items) | *(not evaluated on final_1)* | — |
| Global-MMLU DE | — (no items) | *(not evaluated on final_1)* | — |
| Global-MMLU EN | — (no items) | *(not evaluated on final_1)* | — |
| MMLU college CS | — (no items) | *(not evaluated on final_1)* | — |
| MMLU comp. sec. | — (no items) | *(not evaluated on final_1)* | — |
| cybersoceval | — (no items) | *(not evaluated on final_1)* | — |
| dev-00000-of-00001 | 85.7% (n=7) | *(not evaluated on final_1)* | — |
| malware_analysis-00000-of- | 20.4% (n=49) | *(not evaluated on final_1)* | — |
| test | — (no items) | *(not evaluated on final_1)* | — |
| test-00000-of-00001 | 87.1% (n=171) | *(not evaluated on final_1)* | — |
| threat_intel_reasoning-000 | 31.8% (n=88) | *(not evaluated on final_1)* | — |
| validation | — (no items) | *(not evaluated on final_1)* | — |

### By coarse taxonomy group

**embedding**

| Coarse group | Base | Fine-tuned | Δ |
| --- | --- | --- | ---: |
| Applications & workplace | 84.9% (n=166) | *(not evaluated on final_1)* | — |
| Defensive controls & hygiene | 83.7% (n=153) | *(not evaluated on final_1)* | — |
| Fundamentals & governance | 81.7% (n=230) | *(not evaluated on final_1)* | — |
| Human & social threats | 82.4% (n=250) | *(not evaluated on final_1)* | — |
| Identity & access | 87.1% (n=140) | *(not evaluated on final_1)* | — |
| Malware & advanced threats | 61.5% (n=169) | *(not evaluated on final_1)* | — |
| Network & secure comms | 95.1% (n=123) | *(not evaluated on final_1)* | — |
| Other | 80.4% (n=51) | *(not evaluated on final_1)* | — |

**nli**

| Coarse group | Base | Fine-tuned | Δ |
| --- | --- | --- | ---: |
| Applications & workplace | 71.1% (n=38) | *(not evaluated on final_1)* | — |
| Defensive controls & hygiene | 58.6% (n=29) | *(not evaluated on final_1)* | — |
| Fundamentals & governance | 57.7% (n=71) | *(not evaluated on final_1)* | — |
| Human & social threats | 60.0% (n=55) | *(not evaluated on final_1)* | — |
| Identity & access | 63.6% (n=33) | *(not evaluated on final_1)* | — |
| Malware & advanced threats | 51.1% (n=47) | *(not evaluated on final_1)* | — |
| Network & secure comms | 68.8% (n=32) | *(not evaluated on final_1)* | — |
| Other | 80.0% (n=10) | *(not evaluated on final_1)* | — |

### By fine-grained topic

**embedding**

| Topic | Base | Fine-tuned | Δ |
| --- | --- | --- | ---: |
| Credential management | 91.4% (n=35) | *(not evaluated on final_1)* | — |
| Social engineering | 80.5% (n=41) | *(not evaluated on final_1)* | — |
| Email | 86.2% (n=29) | *(not evaluated on final_1)* | — |
| Defensive measures | 68.2% (n=44) | *(not evaluated on final_1)* | — |
| General hygiene | 72.7% (n=11) | *(not evaluated on final_1)* | — |
| Psychological manipulation | 91.3% (n=46) | *(not evaluated on final_1)* | — |
| Internal risks | 84.4% (n=32) | *(not evaluated on final_1)* | — |
| Foundational concepts | 85.1% (n=67) | *(not evaluated on final_1)* | — |
| Infrastructure protection | 93.2% (n=44) | *(not evaluated on final_1)* | — |
| Authentication/Authorization | 88.7% (n=62) | *(not evaluated on final_1)* | — |
| Regulatory/Legal | 66.7% (n=48) | *(not evaluated on final_1)* | — |
| Firewalls | 96.9% (n=32) | *(not evaluated on final_1)* | — |
| Virus Scans | 64.3% (n=14) | *(not evaluated on final_1)* | — |
| USB safety | 100.0% (n=5) | *(not evaluated on final_1)* | — |
| Encrypted vaults | 72.7% (n=11) | *(not evaluated on final_1)* | — |
| SSL certificates | 100.0% (n=36) | *(not evaluated on final_1)* | — |
| Location leaks | 95.8% (n=24) | *(not evaluated on final_1)* | — |
| Friend requests | 90.9% (n=11) | *(not evaluated on final_1)* | — |
| Unique logins | 91.7% (n=12) | *(not evaluated on final_1)* | — |
| Default usernames | 80.0% (n=20) | *(not evaluated on final_1)* | — |
| Header checks | 95.5% (n=22) | *(not evaluated on final_1)* | — |
| Typos | 88.9% (n=18) | *(not evaluated on final_1)* | — |
| Domains | 77.4% (n=31) | *(not evaluated on final_1)* | — |
| General theory | 88.5% (n=61) | *(not evaluated on final_1)* | — |
| Viruses/Trojans | 61.5% (n=39) | *(not evaluated on final_1)* | — |
| Adware | 80.0% (n=10) | *(not evaluated on final_1)* | — |
| Safe browsing | 93.8% (n=16) | *(not evaluated on final_1)* | — |
| Backups & recovery | 96.8% (n=31) | *(not evaluated on final_1)* | — |
| Advanced cyber threats | 60.7% (n=56) | *(not evaluated on final_1)* | — |
| Advanced malware types | 59.4% (n=64) | *(not evaluated on final_1)* | — |
| Secure communication | 93.0% (n=43) | *(not evaluated on final_1)* | — |
| Professional perspective | 83.3% (n=54) | *(not evaluated on final_1)* | — |
| App security | 83.9% (n=56) | *(not evaluated on final_1)* | — |
| Behavioral security | 67.3% (n=52) | *(not evaluated on final_1)* | — |
| Remote/Traveling security | 80.6% (n=36) | *(not evaluated on final_1)* | — |
| Working from home | 83.3% (n=18) | *(not evaluated on final_1)* | — |
| Other | 80.4% (n=51) | *(not evaluated on final_1)* | — |

**nli**

| Topic | Base | Fine-tuned | Δ |
| --- | --- | --- | ---: |
| Credential management | 53.8% (n=13) | *(not evaluated on final_1)* | — |
| Social engineering | 50.0% (n=16) | *(not evaluated on final_1)* | — |
| Email | 100.0% (n=6) | *(not evaluated on final_1)* | — |
| Defensive measures | 33.3% (n=15) | *(not evaluated on final_1)* | — |
| General hygiene | 100.0% (n=4) | *(not evaluated on final_1)* | — |
| Psychological manipulation | 90.0% (n=10) | *(not evaluated on final_1)* | — |
| Internal risks | 100.0% (n=3) | *(not evaluated on final_1)* | — |
| Foundational concepts | 55.0% (n=20) | *(not evaluated on final_1)* | — |
| Infrastructure protection | 65.0% (n=20) | *(not evaluated on final_1)* | — |
| Authentication/Authorization | 68.4% (n=19) | *(not evaluated on final_1)* | — |
| Regulatory/Legal | 52.9% (n=17) | *(not evaluated on final_1)* | — |
| Firewalls | 100.0% (n=2) | *(not evaluated on final_1)* | — |
| Virus Scans | 50.0% (n=4) | *(not evaluated on final_1)* | — |
| USB safety | — (no items) | *(not evaluated on final_1)* | — |
| Encrypted vaults | 100.0% (n=1) | *(not evaluated on final_1)* | — |
| SSL certificates | 83.3% (n=6) | *(not evaluated on final_1)* | — |
| Location leaks | 72.7% (n=11) | *(not evaluated on final_1)* | — |
| Friend requests | 33.3% (n=3) | *(not evaluated on final_1)* | — |
| Unique logins | — (no items) | *(not evaluated on final_1)* | — |
| Default usernames | — (no items) | *(not evaluated on final_1)* | — |
| Header checks | — (no items) | *(not evaluated on final_1)* | — |
| Typos | — (no items) | *(not evaluated on final_1)* | — |
| Domains | 40.0% (n=5) | *(not evaluated on final_1)* | — |
| General theory | 50.0% (n=20) | *(not evaluated on final_1)* | — |
| Viruses/Trojans | 52.6% (n=19) | *(not evaluated on final_1)* | — |
| Adware | — (no items) | *(not evaluated on final_1)* | — |
| Safe browsing | 100.0% (n=2) | *(not evaluated on final_1)* | — |
| Backups & recovery | 100.0% (n=2) | *(not evaluated on final_1)* | — |
| Advanced cyber threats | 36.4% (n=11) | *(not evaluated on final_1)* | — |
| Advanced malware types | 58.8% (n=17) | *(not evaluated on final_1)* | — |
| Secure communication | 66.7% (n=6) | *(not evaluated on final_1)* | — |
| Professional perspective | 78.6% (n=14) | *(not evaluated on final_1)* | — |
| App security | 61.1% (n=18) | *(not evaluated on final_1)* | — |
| Behavioral security | 46.7% (n=15) | *(not evaluated on final_1)* | — |
| Remote/Traveling security | 80.0% (n=5) | *(not evaluated on final_1)* | — |
| Working from home | 100.0% (n=1) | *(not evaluated on final_1)* | — |
| Other | 80.0% (n=10) | *(not evaluated on final_1)* | — |

![qwen_baronllm tasks](../figures/eval_1/qwen_baronllm_tasks.png)
![qwen_baronllm sources](../figures/eval_1/qwen_baronllm_sources.png)
![qwen_baronllm coarse topics](../figures/eval_1/qwen_baronllm_coarse.png)
![qwen_baronllm fine topics](../figures/eval_1/qwen_baronllm_topics.png)

---

## Llama 3.3 70B Instruct (base) → Trendyol Cyber. LLM v2 (70B)

- **Base model:** `llama-3.3-70b-instruct` — Llama 3.3 70B Instruct (base)
- **Fine-tuned model:** `trendyol-cyber-70b` — Trendyol Cyber. LLM v2 (70B)
- **Backend:** `openai`

### Evaluation status on `data/final_1`

| Classifier corpus | Base evaluated? | Fine-tuned evaluated? |
| --- | --- | --- |
| embedding | yes — 75.7%, n=1353 | **pending** |
| nli | yes — 55.7%, n=327 | **pending** |

### Overall accuracy

| Corpus | Llama 3.3 70B Instruct (base) | Trendyol Cyber. LLM v2 (70B) | Δ |
| --- | --- | --- | ---: |
| embedding | 75.7% (n=1353) | *(not evaluated on final_1)* | — |
| nli | 55.7% (n=327) | *(not evaluated on final_1)* | — |

### By task type

**embedding**

| Task type | Base | Fine-tuned | Δ |
| --- | --- | --- | ---: |
| code_configuration_analysis | 100.0% (n=4) | *(not evaluated on final_1)* | — |
| german_h5p_generation | 100.0% (n=1) | *(not evaluated on final_1)* | — |
| h5p_mcq_generation | 100.0% (n=6) | *(not evaluated on final_1)* | — |
| h5p_structured_generation | 50.0% (n=2) | *(not evaluated on final_1)* | — |
| mcq_answering | 65.7% (n=819) | *(not evaluated on final_1)* | — |
| mcq_generation | 100.0% (n=1) | *(not evaluated on final_1)* | — |
| mitigation_defense_strategy | 83.7% (n=49) | *(not evaluated on final_1)* | — |
| open_explanation | 91.7% (n=471) | *(not evaluated on final_1)* | — |

**nli**

| Task type | Base | Fine-tuned | Δ |
| --- | --- | --- | ---: |
| code_configuration_analysis | — (no items) | *(not evaluated on final_1)* | — |
| german_h5p_generation | — (no items) | *(not evaluated on final_1)* | — |
| h5p_mcq_generation | — (no items) | *(not evaluated on final_1)* | — |
| h5p_structured_generation | — (no items) | *(not evaluated on final_1)* | — |
| mcq_answering | 55.7% (n=327) | *(not evaluated on final_1)* | — |
| mcq_generation | — (no items) | *(not evaluated on final_1)* | — |
| mitigation_defense_strategy | — (no items) | *(not evaluated on final_1)* | — |
| open_explanation | — (no items) | *(not evaluated on final_1)* | — |

### By upstream source

**embedding**

| Source | Base | Fine-tuned | Δ |
| --- | --- | --- | ---: |
| CyberMetric | 90.9% (n=318) | *(not evaluated on final_1)* | — |
| CyberMetric-10000-v1 | 93.4% (n=152) | *(not evaluated on final_1)* | — |
| Global-MMLU DE | 72.9% (n=203) | *(not evaluated on final_1)* | — |
| Global-MMLU EN | 84.1% (n=113) | *(not evaluated on final_1)* | — |
| MMLU college CS | 69.0% (n=42) | *(not evaluated on final_1)* | — |
| MMLU comp. sec. | 88.6% (n=175) | *(not evaluated on final_1)* | — |
| cybersoceval | 22.2% (n=126) | *(not evaluated on final_1)* | — |
| dev-00000-of-00001 | 100.0% (n=2) | *(not evaluated on final_1)* | — |
| malware_analysis-00000-of- | 36.8% (n=19) | *(not evaluated on final_1)* | — |
| test | 82.4% (n=17) | *(not evaluated on final_1)* | — |
| test-00000-of-00001 | 73.9% (n=142) | *(not evaluated on final_1)* | — |
| threat_intel_reasoning-000 | 23.8% (n=42) | *(not evaluated on final_1)* | — |
| validation | 0.0% (n=2) | *(not evaluated on final_1)* | — |

**nli**

| Source | Base | Fine-tuned | Δ |
| --- | --- | --- | ---: |
| CyberMetric | — (no items) | *(not evaluated on final_1)* | — |
| CyberMetric-10000-v1 | — (no items) | *(not evaluated on final_1)* | — |
| Global-MMLU DE | — (no items) | *(not evaluated on final_1)* | — |
| Global-MMLU EN | — (no items) | *(not evaluated on final_1)* | — |
| MMLU college CS | — (no items) | *(not evaluated on final_1)* | — |
| MMLU comp. sec. | — (no items) | *(not evaluated on final_1)* | — |
| cybersoceval | — (no items) | *(not evaluated on final_1)* | — |
| dev-00000-of-00001 | 100.0% (n=7) | *(not evaluated on final_1)* | — |
| malware_analysis-00000-of- | 9.8% (n=51) | *(not evaluated on final_1)* | — |
| test | — (no items) | *(not evaluated on final_1)* | — |
| test-00000-of-00001 | 79.9% (n=174) | *(not evaluated on final_1)* | — |
| threat_intel_reasoning-000 | 32.6% (n=95) | *(not evaluated on final_1)* | — |
| validation | — (no items) | *(not evaluated on final_1)* | — |

### By coarse taxonomy group

**embedding**

| Coarse group | Base | Fine-tuned | Δ |
| --- | --- | --- | ---: |
| Applications & workplace | 75.7% (n=173) | *(not evaluated on final_1)* | — |
| Defensive controls & hygiene | 78.1% (n=160) | *(not evaluated on final_1)* | — |
| Fundamentals & governance | 66.9% (n=242) | *(not evaluated on final_1)* | — |
| Human & social threats | 81.6% (n=272) | *(not evaluated on final_1)* | — |
| Identity & access | 89.4% (n=151) | *(not evaluated on final_1)* | — |
| Malware & advanced threats | 58.4% (n=178) | *(not evaluated on final_1)* | — |
| Network & secure comms | 89.5% (n=124) | *(not evaluated on final_1)* | — |
| Other | 64.2% (n=53) | *(not evaluated on final_1)* | — |

**nli**

| Coarse group | Base | Fine-tuned | Δ |
| --- | --- | --- | ---: |
| Applications & workplace | 60.0% (n=40) | *(not evaluated on final_1)* | — |
| Defensive controls & hygiene | 60.0% (n=30) | *(not evaluated on final_1)* | — |
| Fundamentals & governance | 43.2% (n=74) | *(not evaluated on final_1)* | — |
| Human & social threats | 68.4% (n=57) | *(not evaluated on final_1)* | — |
| Identity & access | 52.9% (n=34) | *(not evaluated on final_1)* | — |
| Malware & advanced threats | 52.1% (n=48) | *(not evaluated on final_1)* | — |
| Network & secure comms | 64.7% (n=34) | *(not evaluated on final_1)* | — |
| Other | 40.0% (n=10) | *(not evaluated on final_1)* | — |

### By fine-grained topic

**embedding**

| Topic | Base | Fine-tuned | Δ |
| --- | --- | --- | ---: |
| Credential management | 91.1% (n=45) | *(not evaluated on final_1)* | — |
| Social engineering | 84.3% (n=51) | *(not evaluated on final_1)* | — |
| Email | 85.3% (n=34) | *(not evaluated on final_1)* | — |
| Defensive measures | 68.8% (n=48) | *(not evaluated on final_1)* | — |
| General hygiene | 81.8% (n=11) | *(not evaluated on final_1)* | — |
| Psychological manipulation | 93.6% (n=47) | *(not evaluated on final_1)* | — |
| Internal risks | 75.8% (n=33) | *(not evaluated on final_1)* | — |
| Foundational concepts | 77.6% (n=67) | *(not evaluated on final_1)* | — |
| Infrastructure protection | 90.9% (n=44) | *(not evaluated on final_1)* | — |
| Authentication/Authorization | 90.3% (n=62) | *(not evaluated on final_1)* | — |
| Regulatory/Legal | 61.8% (n=55) | *(not evaluated on final_1)* | — |
| Firewalls | 93.8% (n=32) | *(not evaluated on final_1)* | — |
| Virus Scans | 64.3% (n=14) | *(not evaluated on final_1)* | — |
| USB safety | 100.0% (n=5) | *(not evaluated on final_1)* | — |
| Encrypted vaults | 81.8% (n=11) | *(not evaluated on final_1)* | — |
| SSL certificates | 88.9% (n=36) | *(not evaluated on final_1)* | — |
| Location leaks | 100.0% (n=24) | *(not evaluated on final_1)* | — |
| Friend requests | 66.7% (n=12) | *(not evaluated on final_1)* | — |
| Unique logins | 100.0% (n=12) | *(not evaluated on final_1)* | — |
| Default usernames | 81.0% (n=21) | *(not evaluated on final_1)* | — |
| Header checks | 95.5% (n=22) | *(not evaluated on final_1)* | — |
| Typos | 78.9% (n=19) | *(not evaluated on final_1)* | — |
| Domains | 65.6% (n=32) | *(not evaluated on final_1)* | — |
| General theory | 58.5% (n=65) | *(not evaluated on final_1)* | — |
| Viruses/Trojans | 65.9% (n=41) | *(not evaluated on final_1)* | — |
| Adware | 80.0% (n=10) | *(not evaluated on final_1)* | — |
| Safe browsing | 81.2% (n=16) | *(not evaluated on final_1)* | — |
| Backups & recovery | 76.5% (n=34) | *(not evaluated on final_1)* | — |
| Advanced cyber threats | 50.0% (n=60) | *(not evaluated on final_1)* | — |
| Advanced malware types | 58.2% (n=67) | *(not evaluated on final_1)* | — |
| Secure communication | 88.6% (n=44) | *(not evaluated on final_1)* | — |
| Professional perspective | 69.1% (n=55) | *(not evaluated on final_1)* | — |
| App security | 78.9% (n=57) | *(not evaluated on final_1)* | — |
| Behavioral security | 74.5% (n=55) | *(not evaluated on final_1)* | — |
| Remote/Traveling security | 59.0% (n=39) | *(not evaluated on final_1)* | — |
| Working from home | 70.0% (n=20) | *(not evaluated on final_1)* | — |
| Other | 64.2% (n=53) | *(not evaluated on final_1)* | — |

**nli**

| Topic | Base | Fine-tuned | Δ |
| --- | --- | --- | ---: |
| Credential management | 38.5% (n=13) | *(not evaluated on final_1)* | — |
| Social engineering | 68.8% (n=16) | *(not evaluated on final_1)* | — |
| Email | 100.0% (n=6) | *(not evaluated on final_1)* | — |
| Defensive measures | 40.0% (n=15) | *(not evaluated on final_1)* | — |
| General hygiene | 100.0% (n=4) | *(not evaluated on final_1)* | — |
| Psychological manipulation | 90.0% (n=10) | *(not evaluated on final_1)* | — |
| Internal risks | 66.7% (n=3) | *(not evaluated on final_1)* | — |
| Foundational concepts | 35.0% (n=20) | *(not evaluated on final_1)* | — |
| Infrastructure protection | 60.0% (n=20) | *(not evaluated on final_1)* | — |
| Authentication/Authorization | 60.0% (n=20) | *(not evaluated on final_1)* | — |
| Regulatory/Legal | 60.0% (n=20) | *(not evaluated on final_1)* | — |
| Firewalls | 100.0% (n=2) | *(not evaluated on final_1)* | — |
| Virus Scans | 50.0% (n=4) | *(not evaluated on final_1)* | — |
| USB safety | — (no items) | *(not evaluated on final_1)* | — |
| Encrypted vaults | 100.0% (n=1) | *(not evaluated on final_1)* | — |
| SSL certificates | 83.3% (n=6) | *(not evaluated on final_1)* | — |
| Location leaks | 81.8% (n=11) | *(not evaluated on final_1)* | — |
| Friend requests | 33.3% (n=3) | *(not evaluated on final_1)* | — |
| Unique logins | — (no items) | *(not evaluated on final_1)* | — |
| Default usernames | — (no items) | *(not evaluated on final_1)* | — |
| Header checks | — (no items) | *(not evaluated on final_1)* | — |
| Typos | — (no items) | *(not evaluated on final_1)* | — |
| Domains | 20.0% (n=5) | *(not evaluated on final_1)* | — |
| General theory | 20.0% (n=20) | *(not evaluated on final_1)* | — |
| Viruses/Trojans | 45.0% (n=20) | *(not evaluated on final_1)* | — |
| Adware | — (no items) | *(not evaluated on final_1)* | — |
| Safe browsing | 100.0% (n=2) | *(not evaluated on final_1)* | — |
| Backups & recovery | 66.7% (n=3) | *(not evaluated on final_1)* | — |
| Advanced cyber threats | 54.5% (n=11) | *(not evaluated on final_1)* | — |
| Advanced malware types | 58.8% (n=17) | *(not evaluated on final_1)* | — |
| Secure communication | 62.5% (n=8) | *(not evaluated on final_1)* | — |
| Professional perspective | 64.3% (n=14) | *(not evaluated on final_1)* | — |
| App security | 40.0% (n=20) | *(not evaluated on final_1)* | — |
| Behavioral security | 64.7% (n=17) | *(not evaluated on final_1)* | — |
| Remote/Traveling security | 80.0% (n=5) | *(not evaluated on final_1)* | — |
| Working from home | 100.0% (n=1) | *(not evaluated on final_1)* | — |
| Other | 40.0% (n=10) | *(not evaluated on final_1)* | — |

![llama33_trendyol tasks](../figures/eval_1/llama33_trendyol_tasks.png)
![llama33_trendyol sources](../figures/eval_1/llama33_trendyol_sources.png)
![llama33_trendyol coarse topics](../figures/eval_1/llama33_trendyol_coarse.png)
![llama33_trendyol fine topics](../figures/eval_1/llama33_trendyol_topics.png)

---

## RoBERTa Base (base) → CyBERTuned

- **Base model:** `roberta-base` — RoBERTa Base (base)
- **Fine-tuned model:** `cybertuned` — CyBERTuned
- **Backend:** `choice_ranking`

### Evaluation status on `data/final_1`

| Classifier corpus | Base evaluated? | Fine-tuned evaluated? |
| --- | --- | --- |
| embedding | **pending** | **pending** |
| nli | **pending** | **pending** |

*Neither side of this pair has been evaluated on `data/final_1` yet. Run both `roberta-base` and `cybertuned` on `data/final_1/{embedding,nli}` before drawing pair conclusions.*

---

## Conclusions from available `final_1` data

### What we can say now (base models only)

- On **embedding / final_1**, **Qwen3 14B (base)** (81.7%, n=1282, OpenRouter) scores higher than **Llama 3.3 70B Instruct (base)** (75.7%, n=1353) by **+6.0 pp** — but this compares two *different* base families, not base vs fine-tuned within a family.
- On **nli / final_1**, Qwen3 14B (base) (61.3%, n=315) vs Llama 3.3 70B Instruct (base) (55.7%, n=327 — partial).

### What we cannot say yet

- Whether cyber fine-tuning helps or hurts on `final_1` — **no fine-tuned model has been run on this dataset**.
- How the 7B families (Mistral→Lily, Zephyr→ZySec, Llama 3.1→Foundation-Sec) behave on the capped corpus.
- Whether encoder tuning (RoBERTa→CyBERTuned) transfers on `final_1`.

## Recommended next steps

1. **Run all six fine-tuned models on `data/final_1`** (`trendyol-cyber-70b`, `baronllm-v2`, `lily-cyber-7b`, `foundation-sec-8b`, `zysec-7b`, `cybertuned`) — both `embedding` and `nli` corpora.
2. **Complete the partial NLI run** for `llama-3.3-70b-instruct` on `final_1`.
3. **Run remaining base models** on `final_1` (Llama 3.1 8B, Mistral 7B, Zephyr 7B, RoBERTa) so every family has both sides on the same pool.
4. **Re-run this script** after each batch; pair Δ columns will populate automatically.
5. **`data/final_combined`** — defer until all `final_1` pairs are complete; that is the next dataset phase, not part of this report.

Per-topic CSV (all pairs × corpora): [`data/eval_1/final_1_by_topic_accuracy.csv`](../data/eval_1/final_1_by_topic_accuracy.csv)

## Regenerate

```bash
.venv/bin/python scripts/interpret_eval_1.py
```
