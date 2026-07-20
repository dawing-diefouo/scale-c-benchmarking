# Scale_C Benchmarking

Reproducible Phase 1 evaluation of language models for the **Scale-C** computer-security education project (H5P-based teaching).

Scale-C may eventually use an LLM to draft content, answer learner questions, and support German material. Before picking a model, we need evidence—not marketing claims—about whether a cybersecurity fine-tuned variant actually beats its base model on Scale-C’s topics. This repository holds the pipeline, frozen Phase 1 evaluation sets, result summaries, and report drafts for that study.

## What Phase 1 covers

Phase 1 is **Tier 1** only: multiple-choice / letter-scored knowledge and reasoning items drawn from public cybersecurity benchmarks, mapped onto Scale-C’s topic taxonomy (37 leaf labels, 28 parent codes, 8 course groups).

Topics were labeled two ways (NLI and embedding similarity), so rankings are not tied to a single automatic classifier:

| View | Scorable items (report denominator) |
|------|-------------------------------------:|
| NLI  | 573 |
| Embedding | 847 |

Tiers 2–3 (structured H5P generation, didactic quality, German localization) are designed but **not** evaluated here. See [docs/design.md](docs/design.md).

## Quick start

```bash
# Python 3.12+ via uv
uv sync
cp .env.example .env   # set OPENROUTER_API_KEY / HF_TOKEN as needed

# Show the Phase 1 pipeline overview
uv run python scripts/run_experiment.py
```

Full reproduction steps (fetch → classify → curate → evaluate → plot): **[docs/reproduce.md](docs/reproduce.md)**.

Evaluate one model on the frozen Phase 1 corpora:

```bash
uv run python scripts/eval_llm_benchmark.py --corpus nli --model qwen3-14b
uv run python scripts/eval_llm_benchmark.py --corpus embedding --model qwen3-14b
```

Regenerate Phase 1 figures from committed summaries:

```bash
uv run python scripts/plot_phase1.py
# → figures/phase1/analysis/
```

## Repository map

| Path | Role |
|------|------|
| [`config/eval_models.json`](config/eval_models.json) | Model registry (base / fine-tuned pairs) |
| [`schema/taxonomy.json`](schema/taxonomy.json) | Scale-C topic taxonomy |
| [`data/phase1/`](data/phase1/) | Frozen Phase 1 eval corpora (`nli/`, `embedding/`) |
| [`data/results/phase1/`](data/results/phase1/) | Per-model `*_summary.json` (+ regenerable `*.jsonl` predictions) |
| [`data/gold_standard/`](data/gold_standard/) | 100-item classification gold standard |
| [`figures/phase1/`](figures/phase1/) | Report figures |
| [`scripts/`](scripts/) | Pipeline entrypoints — see [`scripts/README.md`](scripts/README.md) |
| [`paper/manuscript/`](paper/manuscript/) | Report chapter drafts |
| [`docs/`](docs/) | Reproduce guide, design notes, gold-standard docs |

Bulky intermediate dumps from earlier runs live in local `_archive/` (gitignored), not in the published tree.

## Main findings (Phase 1)

Fine-tuning did **not** help uniformly. Some pairs improved on both classifiers (e.g. Mistral→Lily, Qwen3→Baron); others got worse (e.g. Llama 3.1→Foundation-Sec, Zephyr→ZySec). Malware and advanced-threat items were hard for every model tested. Details are in [`paper/manuscript/`](paper/manuscript/) and the Word report under [`paper/report/`](paper/report/).

## Citation

See [`CITATION.cff`](CITATION.cff). If you use this code or the Phase 1 numbers, please cite the Scale-C benchmarking report.

## Security note

Never commit API keys. Use `.env` (see [`.env.example`](.env.example)). If a key was ever stored in the working tree, rotate it.
