#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

# Suggested: CUDA_VISIBLE_DEVICES=1
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-1}"

exec .venv/bin/python scripts/classify_zero_shot.py \
  --method generative \
  --model sknow-lab/Qwen2.5-14B-CIC-ACLARC \
  --input data/raw/huggingface/cybersoceval \
  --output-root qwen \
  --truncate \
  --device cuda
