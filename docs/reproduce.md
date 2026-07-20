# Reproducing Phase 1

This guide reproduces the **Phase 1 Tier 1** MCQ evaluation reported in the Scale-C benchmarking study.

Expected scorable denominators (Table 4.1):

- **NLI:** 573 items  
- **Embedding:** 847 items  

Committed result summaries under `data/results/phase1/` already reflect those pools. Re-running models from scratch needs GPUs and/or API access and can take many hours.

## 0. Environment

```bash
uv sync
cp .env.example .env
```

Useful variables:

| Variable | Used for |
|----------|----------|
| `OPENROUTER_API_KEY` | API-backed models; gold-standard classification |
| `HF_TOKEN` | Gated Hugging Face models |
| `HF_HOME` / `HF_HUB_CACHE` | Local Hub cache if `~/.cache` is not writable |

Model aliases and serving notes: [`config/eval_models.json`](../config/eval_models.json).

## 1. Upstream data

```bash
uv run python scripts/fetch_datasets.py
uv run python scripts/convert_to_jsonl.py data/raw
```

Raw sources land in `data/raw/`. See [`data/README.md`](../data/README.md).

## 2. Topic classification

Classify processed items against [`schema/taxonomy.json`](../schema/taxonomy.json):

```bash
uv run python scripts/classify_zero_shot.py --help
# One dataset: ./scripts/batch/classify_qwen.sh CyberMetric
# All eight:   ./scripts/batch/run_qwen_all.sh --bg
```

NLI and embedding paths write under `data/processed/`. Intermediate JSONL is regenerable and typically gitignored.

## 3. Build frozen Phase 1 corpora

Default build keeps up to 10 highest-scoring items per (benchmark, topic):

```bash
# Embedding-labeled view
uv run python scripts/build_phase1_dataset.py \
  --input data/processed \
  --output data/phase1/embedding \
  --exclude-benchmark qwen \
  --exclude-benchmark qwen_1 \
  --exclude-benchmark qwen_combined

# NLI-labeled view (Qwen / NLI classified tree)
uv run python scripts/build_phase1_dataset.py \
  --input data/processed/<nli-classified-root> \
  --output data/phase1/nli
```

The repository already ships the frozen corpora used for the report under `data/phase1/{nli,embedding}/`. Prefer those unless you intentionally rebuild.

## 4. Evaluate models

```bash
uv run python scripts/eval_llm_benchmark.py --corpus nli --model qwen3-14b
uv run python scripts/eval_llm_benchmark.py --corpus embedding --model qwen3-14b
```

Defaults:

- Input: `data/phase1/<corpus>/`
- Output: `data/results/phase1/<corpus>/` (`*.jsonl` predictions + `*_summary.json`)

Repeat for each alias in `config/eval_models.json`, or omit `--model` to run the script’s default set.

**Caveats from the report**

- Llama 3.3 70B Instruct NLI stopped early (~327 scorable); do not over-interpret that pair until re-run.
- BaronLLM v2 may be a few items short after transient API failures.

## 5. Figures

```bash
uv run python scripts/plot_phase1.py
# → figures/phase1/analysis/
```

## 6. Classification gold standard (optional)

```bash
export OPENROUTER_API_KEY=...
uv run python scripts/build_mcq_gold_standard.py
```

See [`docs/classification_gold_standard.md`](classification_gold_standard.md). Artifacts: `data/gold_standard/`.

## Sanity checks

After a full eval, each completed model’s `*_summary.json` should report:

```text
nli       totals.scorable ≈ 573
embedding totals.scorable ≈ 847
```

Pipeline overview without running anything:

```bash
uv run python scripts/run_experiment.py
```
