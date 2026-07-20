#!/usr/bin/env python3
"""Print the Phase 1 reproduction pipeline (fetch → classify → curate → eval → plot).

This is a documentation entrypoint, not a full end-to-end runner: classification
and LLM evaluation need GPUs / API keys and take hours. See docs/reproduce.md.
"""

from __future__ import annotations

import sys


STEPS = """
Scale_C Phase 1 pipeline
========================

1) Install
   uv sync
   cp .env.example .env   # set OPENROUTER_API_KEY / HF_TOKEN as needed

2) Fetch and normalize upstream sources
   uv run python scripts/fetch_datasets.py
   uv run python scripts/convert_to_jsonl.py data/raw

3) Topic classification (NLI and/or embedding zero-shot)
   uv run python scripts/classify_zero_shot.py --help
   # GPU batch: ./scripts/batch/classify_qwen.sh <dataset>
   #            ./scripts/batch/run_qwen_all.sh --bg

4) Build the frozen Phase 1 corpora (topic-capped)
   uv run python scripts/build_phase1_dataset.py \\
     --input data/processed --output data/phase1/embedding
   uv run python scripts/build_phase1_dataset.py \\
     --input data/processed/<nli-source> --output data/phase1/nli

5) Evaluate models
   uv run python scripts/eval_llm_benchmark.py --corpus embedding --model qwen3-14b
   uv run python scripts/eval_llm_benchmark.py --corpus nli --model qwen3-14b
   # Outputs: data/results/phase1/<corpus>/

6) Figures
   uv run python scripts/plot_phase1.py
   # Outputs: figures/phase1/analysis/

Expected Phase 1 scorable denominators (report Table 4.1):
  NLI: 573   Embedding: 847

Script index: scripts/README.md
Full walkthrough: docs/reproduce.md
"""


def main() -> None:
    print(STEPS.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
