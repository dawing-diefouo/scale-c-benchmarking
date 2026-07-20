# Scale_C evaluation design (short)

Scale_C evaluates models for an H5P-based computer-security course—not only on what they know, but on what they can do when authoring and supporting learning content.

## Capability tiers

| Tier | Focus | Phase 1 status |
|------|--------|----------------|
| **1** | Factual cyber competence (MCQ, explanations, scenario reasoning, safety judgment) | **Evaluated** in this repo |
| **2** | Structured educational generation (valid H5P / MCQ / cloze JSON, didactic quality) | Designed; schemas under `schema/future/` |
| **3** | Multilingual / German localization (optional) | Designed; not yet run |

A useful rule of thumb for a later overall score (not used in Phase 1 ranking):

```text
Scale_C Score ≈ 0.40 × Tier1 + 0.50 × Tier2 + 0.10 × Tier3
```

## Why compare base vs fine-tuned pairs?

Leaderboard-style single-model scores mix architecture, size, and training. We hold the eval set fixed and compare each cybersecurity-adapted model to its closest base model so gaps are more likely to reflect the adaptation step.

Pairs are registered in [`config/eval_models.json`](../config/eval_models.json).

## Topic taxonomy

Items are mapped to leaf labels in [`schema/taxonomy.json`](../schema/taxonomy.json) (SCLC\* ids), rolled up to parent codes and eight course groups (`schema/taxonomy_coarse.json`). Phase 1 reports NLI and embedding views separately because automatic topic assignment is imperfect.

## Item schema

Records follow the unified Scale_C JSON shape in [`schema/schema.json`](../schema/schema.json): `metadata`, `payload`, and `evaluation` blocks, stored as JSONL for modularity.

The longer German design notes formerly in the root README are archived conceptually here; operational reproduction steps live in [`reproduce.md`](reproduce.md).
