# Chapter 8 — Where models win and lose (course and topic breakdown)

Replace **Section 8** in `Scale-C_Final_Report (1).docx`.  
Citations **[8]**, **[9]**, **[10]**, **[11]** — see `report-references.md`.  
Tone matches `report-chapter6-draft.md` and `report-chapter7-draft.md`.

**Proposed section title (replaces “Course-Level and Topic-Level Patterns”):**

> **8. Where do models win and lose? Course and topic breakdown**

Section 7 showed whether fine-tuning helped **on average**. This section zooms in: **which parts of the Scale-C curriculum** each model handles well, and where adaptation helps or hurts on specific topics.

---

## 8. Where do models win and lose? Course and topic breakdown

Global accuracy hides the pattern Scale-C actually cares about. A model can look fine overall yet fail on malware questions, email phishing, or regulatory content—the kinds of units we teach in different H5P modules.

We break Phase 1 results down in two layers:

1. **Eight course groups** — coarse buckets aligned with `schema/taxonomy_coarse.json` (Option A rollup used in the pipeline).
2. **28 fine topic codes** — parent labels from `schema/taxonomy.json` (e.g. SSL certificates, Advanced malware types).

Topic assignment still depends on the classifier view (NLI or embedding) [9], [10]. Course and topic numbers below come from `data/eval_1/*/ *_summary.json` (`by_topic` rolled up to courses). Support counts (n) are shown where they matter; small n means noisy estimates.

### 8.1 Course-level picture

#### Strong areas: identity, network, and structured facts

At the **embedding** view, the best models cluster on course groups that reward factual, well-covered knowledge:

**Table 8.1 — Strongest course groups (embedding view, selected models)**

| Course group | Llama 3.3 70B | Trendyol 70B | Llama 3.1 8B | Lily 7B |
|--------------|---------------|--------------|--------------|---------|
| Identity & access | 89.4% (n=151) | 68.4% (n=82) | 72.0% (n=82) | 63.4% (n=82) |
| Network & secure comms | 89.5% (n=124) | 81.6% (n=76) | 69.7% (n=76) | 63.2% (n=76) |

These groups cover credentials, authentication, firewalls, TLS, and secure communication—topics that appear often in general pretraining and in standard security curricula [11]. For Scale-C, that is encouraging: **quiz-style content on access control and network hygiene is where current LLMs are least embarrassing**, including at 7B if we pick the right pair (Lily over raw Mistral, Section 7).

#### Weak areas: malware, theory, and mixed “fundamentals”

Across **ten generative models** averaged on embedding labels, the lowest course groups are:

| Course group | Avg. accuracy (generative models) |
|--------------|-----------------------------------|
| Malware & advanced threats | 42.1% |
| Fundamentals & governance | 44.7% |
| Other | 46.4% |
| Applications & workplace | 46.5% |

Even **Llama 3.3 70B**—our strongest absolute model—only reaches **58.4%** on Malware & advanced threats (n=178 embedding), while sitting near 89% on identity and network. The gap is not a quirk of one bad model; it shows up everywhere we looked.

That matters for Scale-C because those course groups map to harder teaching units: threat reasoning, malware families, governance, app security, remote work. **We should not auto-generate those activities without human review**, no matter what the overall leaderboard says.

#### Qwen3: weak everywhere, not just on average

Qwen3 14B is a useful cautionary tale at course level. Under embedding, its best course group (Human & social threats) is still only **16.9%** (n=177). Identity & access is **8.5%**. Section 7 showed Baron lifts the global score, but Baron does not magically fix every course group—only selected topics (below).

**[F10] Course-level accuracy heatmap (NLI and embedding)**

![Figure F10 — Course heatmaps](../../figures/eval_1/analysis/05_course_heatmap_nli_embedding.png)

*Caption:* Eight course groups (rows) × twelve models (columns), split into NLI-classified (left) and embedding-classified (right) corpora. Green cells: higher accuracy; red: lower. Malware & advanced threats and fundamentals rows stay darker across models; identity and network rows light up for larger models. Source: `data/eval_1`, `schema/taxonomy_coarse.json`.

**[F16] Hardest course groups (average across models)**

![Figure F16 — Course difficulty](../../figures/eval_1/analysis/08_course_difficulty_average.png)

*Caption:* Mean course-group accuracy averaged across generative models—useful single glance at where the benchmark stresses every candidate. Optional in Word if F10 is enough.

### 8.2 Hardest fine topics (absolute performance)

Three topics show up repeatedly as pain points. Table 8.2 gives NLI / embedding accuracy for four models on the same fine labels (support counts in parentheses).

**Table 8.2 — Difficult fine topics (NLI% / Emb.% )**

| Topic | Qwen3 14B | BaronLLM v2 | Llama 3.1 8B | Llama 3.3 70B |
|-------|-----------|-------------|--------------|---------------|
| General theory | 8% / 6% (40/31) | 21% / 26% (39/31) | 48% / 58% (40/31) | 20% / 58% (20/65) † |
| Advanced cyber threats | 7% / 16% (15/32) | 20% / 28% (15/32) | 40% / 62% (15/32) | 55% / 50% (11/60) † |
| Advanced malware types | 7% / 9% (29/33) | 28% / 16% (29/32) | 69% / 39% (29/33) | 59% / 58% (17/67) † |

† Llama 3.3 NLI counts reflect the partial run (Section 6.2); embedding denominators differ for this model.

**Reading this for Scale-C**

- **Theory and advanced threats** reward scale and broad pretraining. Llama 3.1 8B often beats Qwen3 and Baron by a wide margin on these slices.
- **Advanced malware** is mixed: under NLI, Lily and Llama 3.1 hit ~69% on their slices—unusually high for this topic—while embedding scores stay lower for most 7B models. The task format and classifier view both shape the story; we should not trust a single number for curriculum planning.
- **Qwen3’s low scores are broad**, not one bad topic. Fixing the serving template might help the base; Baron’s fine-tuning only partially closes the gap.

**[F11] Fine-topic accuracy by model (embedding view)**

![Figure F11 — Topic heatmap](../../figures/eval_1/analysis/12_embedding_topic_model_heatmap.png)

*Caption:* Fine-grained topic codes (rows) vs models (columns), embedding-classified corpus. Malware and threat rows stay consistently dark; identity, network, and SSL-related rows brighten for larger or better-matched models. Qwen3 column is near-uniformly weak. Source: `data/eval_1/embedding/*_summary.json`.

### 8.3 Topic-level fine-tuning: gains and losses

Section 7 reported **global** Δ per pair. Here we show that **topic-level Δ can flip sign inside the same pair**—a model can gain on malware yet lose on email in the same evaluation run.

We highlight pairs with min **n ≥ 5** per side on the stated classifier view. Percentages are topic accuracy; Δ is fine-tuned minus base.

#### Mistral → Lily (consistent global win, mixed topics)

| Classifier | Topic | Base → FT | Δ |
|------------|-------|-----------|---|
| NLI | Advanced malware types | 41% → 69% (n=29) | **+27.6 pp** |
| NLI | Encrypted vaults | 60% → 90% (n=10) | +30.0 pp |
| NLI | Email | 82% → 64% (n=11) | −18.2 pp |
| Embedding | Social engineering | 47% → 74% (n=19) | +26.3 pp |
| Embedding | Typos | 26% → 53% (n=19) | +26.3 pp |

Lily’s global +7 pp (Section 7) is real, and the malware bump is especially relevant for Scale-C—but **Lily gives back ground on some human-factors items** where Mistral was already decent.

#### Qwen3 → Baron (large recovery on hygiene topics)

| Classifier | Topic | Base → FT | Δ |
|------------|-------|-----------|---|
| NLI | Safe browsing | 8% → 82% (n=12/11) | **+73.5 pp** |
| NLI | General hygiene | 20% → 80% (n=5) | +60.0 pp |
| Embedding | Safe browsing | 0% → 38% (n=13) | +38.5 pp |
| Embedding | Location leaks | 6% → 44% (n=18) | +38.9 pp |

These swings likely reflect **overlap between Baron’s training data and safe-computing topics** in the benchmark [7]. They do not mean Baron is uniformly strong—many topics move little or not at all.

#### Llama 3.3 → Trendyol (classifier split starts at topic level)

| Classifier | Topic | Base → FT | Δ |
|------------|-------|-----------|---|
| NLI | Other | 40% → 80% (n=10/30) | +40.0 pp |
| NLI | Domains | 20% → 67% (n=5/15) | +46.7 pp |
| Embedding | Social engineering | 84% → 58% (n=51/19) | **−26.4 pp** |
| Embedding | Default usernames | 81% → 50% (n=21/14) | −31.0 pp |

Trendyol can look like a clear win under NLI topic slices while **losing on social-engineering content under embedding**—the same pair that splits globally in Section 7. For Scale-C units on phishing and user manipulation, that regression is not a small detail.

#### Zephyr → ZySec (regression spreads across topics)

| Classifier | Topic | Base → FT | Δ |
|------------|-------|-----------|---|
| NLI | Email | 64% → 27% (n=11) | **−36.4 pp** |
| NLI | Foundational concepts | 42% → 10% (n=40) | −32.5 pp |
| Embedding | Regulatory/Legal | 64% → 24% (n=25) | −40.0 pp |
| Embedding | Typos | 68% → 32% (n=19) | −36.8 pp |

ZySec’s global −7 to −11 pp is backed by **wide topic-level damage**, including email and foundations—core Scale-C territory.

#### Llama 3.1 → Foundation-Sec (global loss, spotty topic wins)

Foundation-Sec improves on a few small slices (e.g. general hygiene +40 pp NLI, n=5) but **drops sharply** on SSL certificates (−40 pp embedding) and general hygiene (−45.5 pp embedding on a different n). Domain pretraining [2] did not translate into steady gains on the topics Scale-C draws from most often.

**[F12] Topic-level fine-tuning deltas by pair**

![Figure F12 — Topic deltas by pair](../../figures/eval_1/analysis/06_topic_finetuning_delta_by_pair.png)

*Caption:* Fine-grained topic Δ (percentage points) for each base → fine-tuned family, with NLI and embedding panels. Shows heterogeneity behind the global bars in Figure F8. Use with support counts from `data/eval_1` summaries before citing extreme swings in the thesis conclusion.

### 8.4 What Scale-C should take from this chapter

1. **Match model to module type.** Identity, network, and certificate-style MCQs are the safest bet for LLM-assisted drafting in Phase 1. Malware, advanced threats, and broad theory need more human oversight.
2. **Never summarize a model in one adjective.** Lily helps on malware but can slip on email. Trendyol gains on some NLI slices yet loses on social engineering under embedding. “Cyber fine-tuned” does not describe *where* it helps.
3. **Always name the classifier view.** Topic labels come from NLI or embedding assignment [9], [10]. A topic gain under one view may not appear under the other.
4. **Use support counts.** Topics with n &lt; 10 (e.g. general hygiene, USB safety) can show ±40 pp swings that are as much noise as signal. Prefer topics with n ≥ 15 when arguing curriculum fit.
5. **Phase 1 is still incomplete for Scale-C.** We have not tested whether strong MCQ topics translate to valid H5P JSON (Tier 2) or German items (Tier 3). A model that shines on SSL MCQs might still break structured export.

### 8.5 Link to research questions

| RQ | Topic/course picture |
|----|----------------------|
| RQ1 | Fine-tuning effects vary by topic inside the same pair—not only by global Δ. |
| RQ2 | Course rankings are broadly similar across classifiers, but **pairwise topic Δ** can disagree (Trendyol, Lily email vs malware). |
| RQ3 | 70B models dominate identity/network slices; 7B models can be competitive on selected topics (Lily on malware NLI) but not on hardest threat theory. |
| RQ4 | Baron closes large gaps on safe-browsing/hygiene topics but remains behind Llama 3.1 / 70B on theory and threats. |

Classifier-level disagreement for the 70B pair is analyzed further in Section 9. Reasoning architecture vs scale on three hard topics is Section 10.

---

## References used in Chapter 8 (summary)

| Ref | Used for |
|-----|----------|
| [2] | Foundation-Sec domain pretraining context |
| [7] | Training-data overlap hypotheses (Baron, Lily) |
| [8] | MCQ accuracy by topic/course |
| [9] | NLI topic labeling |
| [10] | Embedding topic labeling |
| [11] | Benchmark source coverage by topic |

---

## Author notes (remove from thesis)

- Align course group names with Figure F10 / `taxonomy_coarse.json` (not the longer Table 4.2 names in Ch. 4 unless you harmonize both).
- Recompute Table 8.2 after Llama 3.3 NLI completes; footnote may be removable.
- If page limit is tight, drop F16 and keep F10 + F12.
- Cross-link Section 7 pairs when inserting into Word (one forward sentence at end of §7.4 is enough).
