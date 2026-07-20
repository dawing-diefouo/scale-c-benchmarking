#!/usr/bin/env bash
# Classify one upstream Hugging Face dataset tree with the Qwen generative classifier.
#
# Usage:
#   ./scripts/batch/classify_qwen.sh CyberMetric
#   CUDA_VISIBLE_DEVICES=2 ./scripts/batch/classify_qwen.sh mmlu
#
# Datasets: SEC-bench mmlu cybersoceval CyberMetric Global-MMLU
#           JSONSchemaBench cyberbench superGLEBer
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

DATASET="${1:-}"
if [[ -z "$DATASET" ]]; then
  echo "Usage: $0 <dataset-name>" >&2
  echo "Example: $0 CyberMetric" >&2
  exit 1
fi

INPUT="data/raw/huggingface/${DATASET}"
if [[ ! -d "$INPUT" ]]; then
  echo "Missing input directory: ${INPUT}" >&2
  exit 1
fi

export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"

exec "${ROOT}/.venv/bin/python" scripts/classify_zero_shot.py \
  --method generative \
  --model sknow-lab/Qwen2.5-14B-CIC-ACLARC \
  --input "${INPUT}" \
  --output-root qwen \
  --truncate \
  --device cuda
