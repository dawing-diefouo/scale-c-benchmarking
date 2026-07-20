# Classification gold standard (MCQ)

Frontier-labeled reference set for evaluating Scale_C **topic** classification on
real multiple-choice questions.

The builder keeps only **MCQs** (no cloze / fill-in-blank), classifies each item
with an OpenRouter frontier model plus a one-line **reason**, and retains up to
100 rows whose topic is **not** `SCLC02801` (Other). Records follow
[`schema/schema.json`](../schema/schema.json) with an extra `classification.reason`
and a `reference` block pointing back to the original dataset line.

## Build the gold standard

```bash
export OPENROUTER_API_KEY=...
uv run python scripts/build_mcq_gold_standard.py
```

Defaults:

| Flag | Default | Purpose |
|------|---------|---------|
| `--datasets` | NLI-classified CyberMetric + mmlu/computer_security | Processed MCQ sources |
| `--count` | `100` | Target size (non-Other only) |
| `--seed` | `42` | Shuffle seed for candidate order |
| `--model` | `anthropic/claude-sonnet-4.6` | OpenRouter model |
| `--output-jsonl` | `data/gold_standard/gold_standard_mcq_100.jsonl` | JSONL output |
| `--output-csv` | `data/gold_standard/gold_standard_mcq_100.csv` | CSV review sheet |
| `--resume` | off | Append; skip questions already in the JSONL |
| `--dry-run` | off | Reuse existing processed labels (no API calls) |

If `data/processed/qwen_combined` is missing, the builder looks under
`_archive/data_processed_qwen_combined` (local archive from the repo cleanup).

## Record layout

Each JSONL row matches `schema/schema.json`:

| Field | Purpose |
|-------|---------|
| `id` | `gold_000001`, … |
| `task_type` | Always `mcq_answering` |
| `payload.question` | MCQ stem |
| `payload.choices` | `{"A": "...", "B": "...", ...}` |
| `evaluation.correct_answer` | Letter key when known |
| `classification.predicted_label` | Frontier topic id (gold label) |
| `classification.predicted_label_name` | Frontier topic name |
| `classification.reason` | Short justification |
| `reference.dataset` | e.g. `CyberMetric`, `mmlu/computer_security` |
| `reference.source_file` | Raw JSONL path under `data/raw/huggingface/` |
| `reference.source_line_no` | 1-based line in the raw file |
| `reference.processed_file` | Classified source under `data/processed/` |
| `reference.original_id` | Scale_C id in the processed corpus |

Use the CSV for quick human review; use the JSONL for programmatic eval.

## Compare against pipeline predictions

```bash
uv run python scripts/export_gold_standard_comparison_xlsx.py
```

Produces:

* `data/gold_standard/gold_standard_mcq_comparison.csv` — side-by-side gold vs embedding vs NLI (fine + **coarse** groups)
* `data/gold_standard/gold_standard_comparison.xlsx` — same data in Excel with summary sheets

Coarse groups are defined in [`schema/taxonomy_coarse.json`](../schema/taxonomy_coarse.json) (8 groups).

Allowed topic label ids and names: [`schema/taxonomy.json`](../schema/taxonomy.json).
