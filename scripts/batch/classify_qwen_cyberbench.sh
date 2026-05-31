#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

# Suggested GPU: 0 (small dataset, 1 jsonl)
GPU="${GPU:-0}"

exec .venv/bin/python scripts/classify_zero_shot.py \
  --method generative \
  --model sknow-lab/Qwen2.5-14B-CIC-ACLARC \
  --input data/raw/huggingface/cyberbench \
  --output-root qwen \
  --truncate \
  --device cuda \
  --gpu "$GPU"
