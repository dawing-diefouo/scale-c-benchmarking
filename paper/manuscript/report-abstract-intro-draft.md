# Proposed replacements — Title, Abstract, Introduction

Use these to replace the corresponding sections in `Scale-C_Final_Report.docx`.

---

## Title (cover page)

**Current (wrong framing):**  
SCALE-C — Benchmarking Cybersecurity Language Models

**Proposed:**

**Benchmarking Language Models for Scale-C**  
*Model selection for H5P-based computer security education*

Optional subtitle:  
*Comparing base and cybersecurity fine-tuned models for the Scale-C teaching platform*

---

## Abstract (replacement draft)

Scale-C is an educational project that teaches computer security through interactive H5P units. The platform may eventually use a large language model to help author content, answer learner questions, and support German-language material. Before committing to a model, we need to know whether a cybersecurity fine-tuned variant actually performs better on Scale-C's tasks than a solid general-purpose base model. That is not a given.

This report describes the benchmarking study we ran to answer that question. We compared six base-and-fine-tuned pairs, from 7B-8B instruction models up to a 70B system. The evaluation set pulls questions from existing cybersecurity benchmarks (MMLU, CyberBench, CyberMetric, CyberSOCEval, SEC-bench, and others) and maps them to Scale-C's topic taxonomy: 37 leaf labels, 28 parent codes, and eight course-level groups. We labeled topics twice, once with natural language inference and once with embedding similarity, so our topic-level results are not tied to a single automatic classifier.

One limitation needs to be stated up front. The numbers in this report come from the first evaluation phase, which is mostly multiple-choice knowledge and reasoning (Scale-C Tier 1). We have not yet run the full evaluation for H5P generation, didactic quality, or German localization (Tiers 2 and 3), even though those tiers are part of the Scale-C blueprint. Any model recommendation here is therefore provisional.

Within the MCQ phase, fine-tuning did not help across the board. Mistral to Lily and Qwen3 to Baron improved on both classifiers. Llama 3.1 to Foundation-Sec and Zephyr to ZySec got worse. The 70B pair (Llama 3.3 to Trendyol) split depending on which classifier we used. Malware and advanced threat questions were hard for every model we tested. Scale-C will need to handle that weakness in its content pipeline no matter which model we pick.

---

## 1. Introduction (replacement draft)

### 1.1 Scale-C: the educational context

Scale-C is a computer security course delivered through H5P interactive units: quizzes, scenarios, explanations, and similar activity types. The content has to be technically correct, usable in a classroom, and valid as H5P. The project exists to teach security, not to benchmark models.

Still, an LLM could be useful for drafting H5P activities, writing multiple-choice distractors, explaining concepts to students, or producing German versions of material. The practical question is simple: which model should Scale-C actually use?

Marketing copy and standalone leaderboard scores will not settle it. A model sold as "cybersecurity fine-tuned" might know the vocabulary but pick wrong answers, output broken JSON, or handle unsafe prompts poorly. A general instruction model might already be good enough. We set up a benchmarking study to test that instead of guessing.

### 1.2 Motivation: why model selection matters for Scale-C

A growing number of language models claim a cybersecurity focus: CyBERTuned, Foundation-Sec, Lily-Cybersecurity, and others. The usual pitch is that training on security data improves reasoning about threats, misconfigurations, and defenses.

For Scale-C, the question is more specific:

> When we hold the evaluation setup constant, does cybersecurity specialization improve the model on what Scale-C actually needs, compared with its base model?

"What Scale-C needs" is broader than multiple-choice recall. Our evaluation blueprint splits capabilities into three tiers: cyber knowledge and reasoning (Tier 1), structured educational output including valid H5P (Tier 2), and optional German localization (Tier 3). This report covers Tier 1 in detail. Tiers 2 and 3 are planned but not yet evaluated. Readers should treat any deployment advice here as incomplete until those tiers are run.

### 1.3 Approach of this benchmarking study

We did not rank cybersecurity models in isolation. Each fine-tuned model is compared against its closest base model: same rough size, same family where possible, same serving setup. That way, a performance gap is more likely to come from the fine-tuning step than from picking a different architecture outright.

The evaluation dataset combines several public benchmark sources rather than a single in-house question bank. We assign each item to a Scale-C topic using two classifiers (NLI and embedding-based zero-shot labeling). For now, model performance means multiple-choice accuracy, broken down by topic and course group so we can see where fine-tuning helps, where it hurts, and where even large models fail.

When the two classifiers disagree on rankings, we treat that as a warning. A model should not be declared the winner for Scale-C if the result flips when we change how topics are labeled, at least not without re-running everything on a fixed item set.

### 1.4 Contributions and report structure

This report provides:

1. A side-by-side comparison of six base/fine-tuned pairs that are realistic options for Scale-C.
2. Evidence that cybersecurity fine-tuning is pair-dependent: it helped some models and hurt others.
3. Topic-level results, including the repeated failure on malware and advanced threat items.
4. A roadmap for the evaluations still missing (H5P generation and localization).

Section 2 covers fine-tuning background for the models we tested. Section 3 states the research questions. Section 4 describes the dataset and taxonomy. Section 5 explains model selection and the evaluation design. Sections 6-11 present MCQ results. Section 12 discusses what this means for Scale-C. Section 13 lists limitations. Section 14 closes with provisional guidance and open work.

---

## Terminology box (insert after Introduction or in a footnote)

| Term | Meaning |
|------|---------|
| Scale-C | The H5P-based computer security education project. |
| Benchmarking study / evaluation framework | The pipeline in this repository for comparing candidate LLMs for Scale-C. |
| Evaluation dataset | Public benchmark items mapped to Scale-C topics; not the same as Scale-C's own course content. |
| Tier 1 / 2 / 3 | Evaluation layers in the Scale-C blueprint: knowledge, H5P generation, localization. |

---

## Naming note (for authors, not thesis body)

Scale-C is the teaching project. This repository and report are the model-comparison work that supports it.

The README also calls the evaluation blueprint "Scale_C", which is easy to confuse with the product name. In the thesis, reserve Scale-C for the platform and use something like "evaluation framework" or "benchmarking study" for the comparison pipeline.
