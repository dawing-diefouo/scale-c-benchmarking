#!/usr/bin/env bash
# Launch all Qwen classification jobs in parallel.
#
# Layout: light benchmarks on busy GPUs 0–1; heavy trees on free GPUs 2–3.
# Preloads the HF model once so parallel jobs share the cache (no 8x download).
#
# Usage:
#   ./scripts/batch/run_qwen_all.sh          # foreground, wait for all
#   ./scripts/batch/run_qwen_all.sh --bg     # background + logs under logs/
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
CLASSIFY="./scripts/batch/classify_qwen.sh"

BACKGROUND=false
if [[ "${1:-}" == "--bg" ]]; then
  BACKGROUND=true
fi

mkdir -p logs

echo "Preloading model..."
if ! ./scripts/batch/preload_qwen_model.sh > logs/qwen_preload.log 2>&1; then
  echo "Model preload failed — see logs/qwen_preload.log"
  exit 1
fi
echo "Model cached ($(du -sh ~/.cache/huggingface 2>/dev/null | cut -f1))."

run_job() {
  local gpu="$1"
  local name="$2"
  if $BACKGROUND; then
    echo "GPU ${gpu}: ${name} -> logs/qwen_${name}.log"
    CUDA_VISIBLE_DEVICES="${gpu}" "${CLASSIFY}" "${name}" > "logs/qwen_${name}.log" 2>&1 &
  else
    echo "GPU ${gpu}: ${name}"
    CUDA_VISIBLE_DEVICES="${gpu}" "${CLASSIFY}" "${name}"
  fi
}

# GPU 0 (busy) — smallest trees
run_job 0 SEC-bench
run_job 0 mmlu

# GPU 1 (busy) — small / medium
run_job 1 cybersoceval
run_job 1 CyberMetric

# GPU 2 (free) — large
run_job 2 cyberbench
run_job 2 Global-MMLU

# GPU 3 (free) — largest
run_job 3 JSONSchemaBench
run_job 3 superGLEBer

if $BACKGROUND; then
  echo "Launched 8 jobs. Tail logs: tail -f logs/qwen_*.log"
  wait
  echo "All Qwen classification jobs finished."
else
  echo "All Qwen classification jobs finished."
fi
