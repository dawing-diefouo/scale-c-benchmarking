# Data layout

```text
data/
├── raw/              # Upstream benchmarks (provenance by source)
├── processed/        # Intermediate classification output (regenerable)
├── gold_standard/    # 100-item MCQ topic-classification gold set
├── phase1/           # Frozen Phase 1 evaluation corpora
│   ├── nli/
│   └── embedding/
└── results/
    └── phase1/       # Model summaries + predictions
        ├── nli/
        └── embedding/
```

## Frozen vs regenerable

| Path | In git? | Notes |
|------|---------|--------|
| `phase1/{nli,embedding}/` | Prefer yes (frozen report inputs) | Topic-capped Tier 1 pools; scorable denominators 573 / 847 |
| `results/phase1/*_summary.json` | Yes | Accuracies and breakdowns for the report |
| `results/phase1/*.jsonl` | No (gitignored) | Per-item predictions; regenerate with `eval_llm_benchmark.py` |
| `processed/**/*.jsonl` | Usually no | Rebuild via classify scripts |
| `raw/` | Partial / large | Prefer fetch scripts; some mirrors may be local-only |
| `gold_standard/` | Yes | Classification validation set |

## Benchmark families in Phase 1

Scorable Tier 1 items mainly come from CyberMetric, CyberSOCEval, Global-MMLU, and MMLU (computer security / college CS). Sources without Tier 1 gold answers (e.g. JSONSchemaBench, superGLEBer, SEC-bench, parts of CyberBench) may still appear in the classified trees for later tiers.

Note: the embedding tree historically used the folder name `cyberbech` (typo for cyberbench). Treat it as a legacy path alias; do not rename without updating manifests and scripts.

## Local archive

Earlier uncapped runs and intermediate trees were moved to repo-local `_archive/` (gitignored), including former `eval_combined`, `final_combined`, and `processed/qwen*` dumps. Safe to delete once you no longer need them.

## GitHub size limits

These Phase 1 trees are kept locally but **not** committed (each exceeds GitHub's 100 MB file limit and they contribute no Tier 1 gold answers):

- `phase1/**/JSONSchemaBench/`
- `phase1/**/cyberbech/`
- `phase1/**/superGLEBer/`

Rebuild them with `scripts/build_phase1_dataset.py` if needed.
