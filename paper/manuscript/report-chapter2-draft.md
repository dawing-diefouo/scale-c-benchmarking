# Chapter 2 — Fine-tuning (replacement draft)

Use this to replace Section 2 in `Scale-C_Final_Report.docx`.  
Citations **[1]–[7]** only — see `report-references.md`.

---

## 2. Fine-tuning background

Scale-C may end up using a model that has been adapted for cybersecurity. Before we compare candidates in later chapters, this section explains what fine-tuning means in practice, which training styles appear in our model pairs, and why adaptation sometimes helps and sometimes makes things worse.

We keep the math light. The goal is not a general machine learning textbook, but enough context to read the pairwise results in Sections 6–11.

### 2.1 Starting from a pre-trained model

Modern NLP systems rarely train from random initialization. A model is first pre-trained on large general text, then adapted to a downstream task [1]. Fine-tuning reuses those pre-trained weights W₀ as the starting point and updates them on a smaller, task-specific dataset.

In notation: W_init = W₀, followed by gradient updates with learning rate η. For fine-tuning, η is usually much smaller than in pre-training [1]. Large steps can damage general capabilities the base model already has; small steps shift behavior toward the target task without relearning everything from scratch.

For Scale-C, that trade-off is concrete. We want domain knowledge and stable answer patterns for quizzes and, later, H5P generation. We do not want a model that forgets instruction following or valid output structure.

### 2.2 Common training objectives

**Supervised fine-tuning (SFT).**  
Given labeled (prompt, target) pairs, training minimizes cross-entropy loss so the model assigns higher probability to the correct tokens. Instruction-tuned models are trained on many formatted tasks so they generalize to new prompts at inference time [3]. Lily and Baron fall in this group according to their published model documentation [7].

**Preference optimization (RLHF and related methods).**  
Some aligned assistants are trained to prefer one response over another. RLHF fits a reward model from human rankings, then fine-tunes the policy while penalizing drift from a reference model, often with a Kullback–Leibler (KL) term [4]:

ℒ_total = ℒ_reward + β · D_KL(P_ref ‖ P_θ)

The risk for Scale-C: a model can sound more helpful or security-aware while becoming worse at picking the right multiple-choice option. We group ZySec here as an assistant-style cyber model [7].

**Continued domain pretraining.**  
A second pretraining phase on in-domain unlabeled text often improves downstream performance over a general model alone [2]. Vocabulary and topic coverage improve, but there is no direct supervision on answer format. Foundation-Sec is our main example in this group [7].

**Parameter-efficient adaptation (LoRA).**  
Full fine-tuning updates every weight. LoRA freezes W₀ and learns a low-rank update ΔW ≈ B·A, which cuts memory use while matching full fine-tuning on several benchmarks [5]. Most open cyber models in our study use LoRA or a similar efficient method [5], [7].

**KL-style regularization (not universal).**  
KL penalties are common in RLHF to keep the model close to its base [4]. Not every cyber model documents this step. We mention it as one possible explanation when a tuned model keeps domain phrasing but loses multiple-choice accuracy, as with Foundation-Sec and ZySec in Section 7.

### 2.3 Adaptation strategies in this study

The six pairs we evaluate do not share one training recipe. Table 2.1 maps each style to Scale-C tasks and to the pairs in this study. Training details for named models come from their Hugging Face documentation [7].

**Table 2.1 — Adaptation strategies and relevance to Scale-C**

| Strategy | Basis in literature | Scale-C tasks it should help | Pair(s) |
|----------|---------------------|------------------------------|---------|
| Encoder domain adaptation | Cyber-domain BERT pretraining [6] | Baseline only; weak fit for generative H5P | RoBERTa → CyBERTuned |
| Continued domain pretraining | DAPT [2] | Tier 1 factual MCQ | Llama 3.1 → Foundation-Sec |
| Instruction SFT on cyber data | Instruction tuning [3] | Tier 1 MCQ; Tier 2 H5P (not yet tested) | Mistral → Lily; Qwen3 → Baron |
| Preference-aligned assistant tuning | RLHF [4] | Learner chat tone; safety (not fully evaluated) | Zephyr → ZySec |
| Large-scale cyber SFT on a strong base | Instruction tuning [3] | Hard Tier 1 topics; possible Tier 2 | Llama 3.3 → Trendyol |

CyBERTuned is not a generative Scale-C candidate [6]. We include it to show how much of the gap comes from architecture (encoder vs. decoder) rather than from cyber fine-tuning alone.

### 2.4 What we should expect before looking at the numbers

Fine-tuning is not a single switch. Domain pretraining can raise topic coverage without fixing output format [2]. Instruction tuning can improve prompt following on new task types [3]. Preference optimization can change style without improving factual benchmarks [4]. LoRA makes these steps practical at 7B–70B scale [5].

In our study, that shows up as gains after instruction tuning (Lily, Baron), regressions after some domain or alignment steps (Foundation-Sec, ZySec), topic-level splits within one pair (Trendyol), and only marginal movement when the architecture is wrong for generative answering (CyBERTuned).

The benchmarking study compares each fine-tuned model to its base under the same evaluation setup. The question is not whether a model is marketed as cyber-themed, but whether adaptation made it better for Scale-C than the base we already had.

Sections 6–11 answer that for Tier 1 multiple-choice items. Tier 2 (H5P JSON, didactic structure) and Tier 3 (German localization) still need their own runs.

### 2.5 Figure

**[F1] Fine-tuning in the Scale-C model-selection context**

```
[Base model W₀] ──fine-tune──> [Cyber-adapted model]
       │                                │
       └──────── same eval items ───────┘
                         │
              Scale-C Tier 1 (MCQ) ──> accuracy delta
              Scale-C Tier 2 (H5P)  ──> (future)
```

Show the pairwise comparison: one base, one adapted variant, shared benchmark items, delta on Scale-C metrics.

---

## Chapter 2 references (summary)

| Ref | Covers |
|-----|--------|
| [1] | Fine-tuning from pre-trained weights |
| [2] | Continued / domain-adaptive pretraining |
| [3] | Instruction tuning and SFT |
| [4] | RLHF and KL regularization |
| [5] | LoRA |
| [6] | CyBERTuned (encoder cyber model) |
| [7] | All six evaluated model cards (Hugging Face) |

---

## Author notes (remove from thesis)

- Confirm ZySec and Trendyol training recipes on Hugging Face before defense.
- Optional appendix: DPO [Rafailov et al.], BERT/RoBERTa encoder background, full LoRA math.
