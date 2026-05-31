#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

# Suggested: CUDA_VISIBLE_DEVICES=0
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"

exec .venv/bin/python scripts/classify_zero_shot.py \
  --method generative \
  --model sknow-lab/Qwen2.5-14B-CIC-ACLARC \
  --input data/raw/huggingface/CyberMetric \
  --output-root qwen \
  --truncate \
  --device cuda
