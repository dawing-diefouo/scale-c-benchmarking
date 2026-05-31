#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

# Suggested: CUDA_VISIBLE_DEVICES=2
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-2}"

exec .venv/bin/python scripts/classify_zero_shot.py \
  --method generative \
  --model sknow-lab/Qwen2.5-14B-CIC-ACLARC \
  --input data/raw/huggingface/Global-MMLU \
  --output-root qwen \
  --truncate \
  --device cuda
