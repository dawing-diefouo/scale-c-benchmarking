# Scale-C Final Report — Redline Checklist

Mapped section-by-section to `Scale-C_Final_Report.docx`.  
Use `[ ]` open / `[x]` done when fixing each item.

**Framing correction (applies globally):** Scale-C is the **educational project** (H5P-based computer security teaching). **This report** describes a **benchmarking study** whose goal is to determine which language model best supports Scale-C. The benchmark pipeline and evaluation framework are the *method*; they are not the same thing as the Scale-C product.

---

## Cover / Title page

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| C-1 | **Critical** | Title *"SCALE-C / Benchmarking Cybersecurity Language Models"* reads as if Scale-C **is** the benchmark. | Retitle, e.g. **"Benchmarking Language Models for Scale-C: Model Selection for H5P-Based Cybersecurity Education"** or **"Evaluating LLMs for the Scale-C Educational Platform"**. |
| C-2 | Medium | Subtitle does not mention H5P, structured content generation, or model-selection purpose. | Add one line: *"A comparative study of base vs. fine-tuned models for cybersecurity teaching with H5P."* |
| C-3 | Low | No author names, supervisor, or repo link. | Add standard thesis metadata + link to `scale-c-benchmarking` repository. |

---

## Abstract

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| A-1 | **Critical** | Opens with *"This report presents Scale-C, a reproducible benchmarking pipeline"* — conflates product and study. | Open with Scale-C as the **target application**, then state this work **evaluates models for it**. |
| A-2 | **Critical** | Claims *"reproducible benchmarking pipeline"* while §13 admits results come from a presentation and are not locally reproducible. | Either remove "reproducible" or qualify: *"toward a reproducible pipeline; current results are provisional."* |
| A-3 | High | No mention of **H5P**, **structured educational generation**, or **Tier 2** (50% weight in Scale-C blueprint). | State that MCQ results are **Phase 1**; full Scale-C suitability requires H5P/didactic evaluation. |
| A-4 | High | *"28 fine-grained topics"* — `schema/taxonomy.json` has **37 leaf labels** and **28 parent codes**. | Use: *"37 topic labels grouped into 28 parent codes (and 8 course groups)"* — or fix counts after taxonomy audit. |
| A-5 | Medium | Findings presented as final though repo `.todo` shows model eval not completed. | Label as *interim MCQ-phase findings* unless results are re-verified from repo. |
| A-6 | Medium | No **model recommendation** sentence for Scale-C stakeholders. | Add one line: which model(s) are leading candidates **for which Scale-C tasks** (even if provisional). |

---

## 1. Introduction

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| I-1 | **Critical** | Scale-C introduced only as a benchmark, not as the **H5P cybersecurity education project** it actually is. | New opening paragraph: what Scale-C teaches, how H5P is used, why an LLM is needed (content generation, Q&A, localization, etc.). |
| I-2 | **Critical** | Motivation is generic ("explosion of cybersecurity LLMs") without tying to **Scale-C's operational needs**. | Motivate from Scale-C: e.g. generating valid H5P units, answering learner questions, German content, safety in classroom context. |
| I-3 | High | *"Scale-C takes a different approach"* — ambiguous; sounds like Scale-C is this paper's invention as a benchmark name. | Split entities: **(a) Scale-C platform**, **(b) this benchmarking study / evaluation framework**. |
| I-4 | High | Lists benchmark sources but not **Scale-C task types** (Tier 1/2/3 from blueprint). | Add paragraph mapping report scope to Scale-C tiers; state which tiers are evaluated in this report (currently: mostly Tier 1 MCQ only). |
| I-5 | Medium | *"28 fine topics and 8 course groups"* — 8 course groups not defined in repo; 37 leaves vs 28 parents conflated. | Define course groups in text or appendix; fix taxonomy counts. |
| I-6 | Medium | Roadmap (§2 fine-tuning theory before problem statement) buries the Scale-C context. | Consider moving condensed Scale-C context before §2, or add forward pointer: *"§2 provides ML background; Scale-C requirements are in §3–4."* |
| I-7 | Low | No explicit **deliverable** of the study (model recommendation for Scale-C deployment). | State deliverable: ranked model pairs by Scale-C-relevant capability, with deployment caveats. |

---

## 2. Fine-Tuning

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| F-1 | Medium | Very long generic ML section; weak link to **Scale-C model-selection decision**. | Shorten or move to appendix; keep §2.5 (four specialization strategies) and tie each to **Scale-C tasks** (e.g. instruction tuning → H5P prompts). |
| F-2 | Medium | KL regularization presented as universal; not all evaluated models use it. | Qualify: *"Some training recipes include KL-style regularization; see per-model notes in §5."* |
| F-3 | Low | Unicode glitch: `Wᴵⁿⁱᵗⁱᵃᱬ` | Replace with `W_init = W₀` or plain text. |
| F-4 | **Critical** | `[F1]` placeholder only — no figure. | Add fine-tuning intuition diagram or remove placeholder. |

---

## 3. Research Objective and Guiding Questions

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| R-1 | **Critical** | Core objective framed as *"determine whether cybersecurity fine-tuning improves… on a benchmark"* — not *"which model best supports Scale-C."* | Reframe primary objective: **select the most suitable LLM for Scale-C** (H5P + cyber competence + optional DE). |
| R-2 | High | RQ1–RQ4 are about fine-tuning effects and classifiers; **no RQ about H5P generation, didactic quality, or safety**. | Add RQ5 (H5P/structure), RQ6 (safety), RQ7 (German) — mark unevaluated if not yet run. |
| R-3 | Medium | Mentions H5P and German in passing but RQs don't test them. | Align listed capabilities with actual research questions. |
| R-4 | Low | `[F2]` placeholder — research design figure missing. | Add base vs fine-tuned vs Scale-C task diagram (not just benchmark pipeline). |

---

## 4. Dataset Construction and Taxonomy

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| D-1 | High | *"Scale-C combines multiple benchmark sources"* — should say the **evaluation dataset for model selection** combines sources **aligned with Scale-C topic coverage**. | Reword to separate dataset from product. |
| D-2 | High | 1,777 / 961 counts vs *"newest evaluation"* — no single authoritative N. | Report exact N from latest manifest; one row per pipeline run. |
| D-3 | High | **Classifier role unclear**: topic assignment vs model scoring conflated later in §9. | Add explicit subsection: classifiers label **items**; MCQ accuracy scores **model answers**; two classifier runs → two topic-labeled datasets. |
| D-4 | High | Non-MCQ items (H5P, open explanations) acknowledged as needing rubrics but **not evaluated** — critical for Scale-C. | Flag as **blocking gap** for Scale-C model choice; don't imply dataset fully represents Scale-C. |
| D-5 | Medium | `superGLEBer` mapped to "Scale-C multilingual tier" — it's general German NLP, not cyber-specific. | Soften claim; note proxy role only. |
| D-6 | Medium | Metadata dimensions (risk, difficulty, cognitive_skill) shown as taxonomy but are **placeholders** in code (`"-"`). | Mark as proposed/unvalidated (as §13 notes) **in §4**, not only in limitations. |
| D-7 | Low | `[F4]`, `[F5]`, `[F6]` placeholders. | Add pipeline, composition, and taxonomy figures. |

---

## 5. Model Selection and Evaluation Design

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| M-1 | High | Pair table is good but missing **training type, serving backend, decoding params** per pair. | Add columns: SFT/DPO/LoRA, temperature, max tokens, prompt template, hardware. |
| M-2 | High | No **selection criteria for Scale-C** (e.g. must run H5P JSON, 7B deployable on X GPU). | Add §5.3: practical constraints for Scale-C deployment. |
| M-3 | Medium | Encoder pair (RoBERTa/CyBERTuned) useful as control but **not a Scale-C candidate** — should be stated explicitly. | One sentence: encoders excluded from deployment recommendation. |
| M-4 | Low | `[F3]` placeholder. | Add model-pair overview figure/table. |

---

## 6. Global Results

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| G-1 | **Critical** | Results sourced from **presentation**, not repo `results/` (empty). | Re-run and commit results; until then, banner: *"Provisional — presentation slides, date YYYY-MM-DD."* |
| G-2 | **Critical** | NLI vs embedding leaders use **different denominators** (Llama 3.3 NLI partial). | Do not rank globally across classifiers without same item set; report n/N per column. |
| G-3 | High | Global accuracy framed as model quality; may reflect **different filtered datasets** per classifier. | Clarify in caption and text. |
| G-4 | Medium | Encoder ~21–27% vs generative ~30–35 pp gap — correct but **not actionable for Scale-C** without generative eval. | Reframe as architecture control finding. |
| G-5 | Low | `[F7]`, `[F9]` placeholders. | Add leaderboard and encoder-gap charts. |

---

## 7. Pairwise Fine-Tuning Effects

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| P-1 | High | Pairwise deltas useful for science but **secondary for Scale-C** if absolute H5P ability matters more. | Add column or note: *"Scale-C deployment relevance."* |
| P-2 | Medium | No significance tests or confidence intervals on deltas. | Add error bars or bootstrap CIs if n allows. |
| P-3 | Medium | Trendyol classifier-split needs **same-item-set** confirmation before recommendation. | Re-evaluate 70B pair on frozen manifest. |
| P-4 | Low | `[F8]` placeholder. | Add delta chart. |

**Interim Scale-C signal (MCQ only, provisional):** Lily and Baron ↑; Foundation-Sec and ZySec ↓; Trendyol inconclusive.

---

## 8. Course-Level and Topic-Level Patterns

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| T-1 | High | Topic deltas (+73.5 pp, etc.) without **support counts** — unreliable for sparse topics. | Add n per cell; suppress or flag low-n slices. |
| T-2 | High | Course groups (*"Identity and Access Management"*, *"Network and Secure Communications"*) **not defined** in repo taxonomy file. | Document mapping from leaf labels → 8 courses in §4 or appendix. |
| T-3 | Medium | Malware/threat weakness relevant to Scale-C content — good — but no link to **which H5P units** would suffer. | Optional: map weak topics to Scale-C curriculum modules. |
| T-4 | Low | `[F10]`, `[F11]`, `[F12]` placeholders. | Add heatmaps and gain/loss panels. |

---

## 9. Classifier Divergence

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| CD-1 | **Critical** | Interprets NLI/embedding as measuring **model output phrasing** — contradicts §4.3 (exact-match MCQ scoring). | Rewrite: disagreement likely from **topic assignment / dataset composition**, unless a separate answer-scoring experiment exists. |
| CD-2 | High | 11 agree / 15 disagree on 70B pair — strong claim without published contingency table. | Add table or move to appendix with counts. |
| CD-3 | Low | `[F13]`, `[F14]` placeholders. | Add ranking divergence and per-topic agreement figures. |

---

## 10. Reasoning Architecture Versus Scale

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| S-1 | High | Compares **across pairs** (Qwen3, Baron, Llama 3.3, Llama 3.1) — breaks pairwise design; confounds size (14B vs 8B vs 70B). | Restrict to within-pair or add size-matched comparison section. |
| S-2 | Medium | "Reasoning-oriented architecture" for Qwen3 is debatable marketing framing. | Use neutral: *"Qwen3 14B base vs Baron fine-tune."* |
| S-3 | Low | `[F15]` placeholder. | Add grouped bar chart. |

---

## 11. The Hardest Benchmark Areas

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| H-1 | High | Qualitative error analysis **explicitly missing** — limits Scale-C content QA insights. | Add F17 table: prompt, gold, model answer, failure mode (min. 5–10 items). |
| H-2 | Medium | Lists hypothetical causes without evidence. | Prioritize error analysis to test each bullet. |
| H-3 | Low | `[F16]`, `[F17]` placeholders. | Add hardest-topics plot and error table. |

---

## 12. Discussion

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| DIS-1 | **Critical** | Five claims are about **fine-tuning science**, not **Scale-C model recommendation**. | Add §12.6: **Implications for Scale-C** — which model for H5P authoring, tutoring, DE, given current evidence. |
| DIS-2 | High | No discussion of **Tier 2 gap** (50% of Scale-C score formula). | State that current report cannot rank models for primary Scale-C use case yet. |
| DIS-3 | Medium | §12.2 encoder conclusion correct but orthogonal to Scale-C product needs. | Move encoder discussion to methodology appendix or shorten. |

---

## 13. Limitations

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| L-1 | **Critical** | Written as meta-instructions (*"should be explicitly acknowledged"*) — not polished thesis prose. | Rewrite in past/present factual voice for submission. |
| L-2 | High | Missing limitation: **scope mismatch** — report title/framing vs actual evaluated tasks (MCQ only). | Add prominently. |
| L-3 | High | Missing limitation: **Scale-C product requirements** (H5P, pedagogy, classroom safety) largely untested. | Add. |
| L-4 | Low | `[F18]` reproducibility table placeholder. | Fill with versions, commits, GPUs, decoding params. |

---

## 14. Conclusion

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| CON-1 | **Critical** | Concludes on fine-tuning question; does **not answer** *"which model should Scale-C use?"* | Add explicit recommendation section: primary candidate, fallback, models to avoid, required follow-up eval. |
| CON-2 | High | Future work lists qualitative analysis but omits **H5P Tier 2 benchmark execution** as top priority. | Reorder future work: (1) H5P eval, (2) safety, (3) DE, (4) error analysis. |
| CON-3 | Medium | Still says *"Scale-C establishes three methodological points"* — sounds like Scale-C = this paper. | Attribute to **this benchmarking study for Scale-C**. |

---

## 15. Figure and Graph Checklist

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| FG-1 | **Critical** | All **18 figures (F1–F18) incomplete** — report not visually submission-ready. | Complete or cut placeholders and references to missing figures. |
| FG-2 | Medium | No figure showing **Scale-C application context** (learner → H5P unit → LLM role). | Add F0 or expand F2: Scale-C system context diagram. |

---

## References

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| REF-1 | **Critical** | *"References to be inserted in IEEE format"* — empty. | Complete IEEE bibliography; cite Hendrycks et al., Rafailov et al., all model cards, frameworks. |

---

## Cross-cutting (entire document)

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| X-1 | **Critical** | **Naming**: "Scale-C" used for product, benchmark framework, and report interchangeably. | Glossary box: **Scale-C** = H5P education project; **evaluation framework / benchmark suite** = name TBD (e.g. "Scale-C Model Evaluation Suite"). |
| X-2 | **Critical** | Repo pipeline incomplete (`.todo`: classify all data, model eval not done). | Align report status with repo state. |
| X-3 | High | No **executive summary table** for stakeholders: Model × Tier1 × Tier2 × Tier3 × Deployability. | Add one-page summary at front. |
| X-4 | High | Weighted Scale-C score formula (40/50/10) never computed. | Compute when Tier 2/3 exist; until then don't imply composite ranking. |
| X-5 | Medium | `classify_zero_shot.py` default model is embedding CLIP model while docstring says NLI — repo inconsistency. | Fix script defaults; document both classifiers in methods. |

---

## Suggested fix order

1. **Reframe title, abstract, introduction** (C-1, A-1, I-1, I-2, X-1)  
2. **Clarify scope**: MCQ Phase 1 vs full Scale-C suitability (A-3, I-4, DIS-2)  
3. **Fix taxonomy counts and course-group definitions** (A-4, D-1, T-2)  
4. **Re-run or label provisional results** (G-1, G-2, L-1)  
5. **Add Scale-C recommendation section** (CON-1, DIS-1)  
6. **Plan Tier 2 H5P evaluation** (blocking for real model choice)  
7. **Figures, references, reproducibility table** (FG-1, REF-1, F18)
