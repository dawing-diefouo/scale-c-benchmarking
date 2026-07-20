# Scripts

Phase 1 entrypoints only. Older one-offs and ops helpers live in `_archive/scripts/`.

## Pipeline

| Script | Role |
|--------|------|
| [`run_experiment.py`](run_experiment.py) | Prints the reproduction steps (does not run GPUs) |
| [`fetch_datasets.py`](fetch_datasets.py) | Download / mirror upstream sources into `data/raw/` |
| [`convert_to_jsonl.py`](convert_to_jsonl.py) | Convert `.json` / `.csv` / `.parquet` → `.jsonl` |
| [`classify_zero_shot.py`](classify_zero_shot.py) | Topic classification → `data/processed/` |
| [`build_phase1_dataset.py`](build_phase1_dataset.py) | Curate frozen Phase 1 corpora → `data/phase1/` |
| [`eval_llm_benchmark.py`](eval_llm_benchmark.py) | Score models → `data/results/phase1/` |
| [`plot_phase1.py`](plot_phase1.py) | Figures → `figures/phase1/analysis/` |

## Gold standard (optional)

| Script | Role |
|--------|------|
| [`build_mcq_gold_standard.py`](build_mcq_gold_standard.py) | Build the 100-item classification gold set |
| [`export_gold_standard_comparison_xlsx.py`](export_gold_standard_comparison_xlsx.py) | Compare gold vs automatic classifiers |

## Batch (GPU classification)

| Script | Role |
|--------|------|
| [`batch/classify_qwen.sh`](batch/classify_qwen.sh) | Classify one dataset with Qwen |
| [`batch/run_qwen_all.sh`](batch/run_qwen_all.sh) | Launch all eight jobs |
| [`batch/run_qwen_light_sequential.sh`](batch/run_qwen_light_sequential.sh) | Light jobs only, sequential per GPU |
| [`batch/preload_qwen_model.sh`](batch/preload_qwen_model.sh) | Warm HF cache once |
| [`batch/GPU_ASSIGNMENTS.md`](batch/GPU_ASSIGNMENTS.md) | GPU layout notes |

## Internal

| File | Role |
|------|------|
| [`_top_n_by_label.py`](_top_n_by_label.py) | Helper imported by `build_phase1_dataset.py` |
