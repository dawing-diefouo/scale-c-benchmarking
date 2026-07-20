#!/usr/bin/env bash
# Run light Qwen jobs sequentially per GPU (one model at a time per GPU).
# GPU 0: SEC-bench -> mmlu
# GPU 1: cybersoceval -> CyberMetric
#
# Usage:
#   ./scripts/batch/run_qwen_light_sequential.sh          # foreground
#   ./scripts/batch/run_qwen_light_sequential.sh --bg     # background
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
CLASSIFY="./scripts/batch/classify_qwen.sh"

if [[ "${1:-}" == "--bg" ]]; then
  mkdir -p logs
  : > logs/qwen_light_sequential.log
  nohup "${BASH_SOURCE[0]}" >> logs/qwen_light_sequential.log 2>&1 &
  echo "Started GPU 0 (SEC-bench->mmlu) + GPU 1 (cybersoceval->CyberMetric) -> logs/qwen_light_sequential.log"
  exit 0
fi

mkdir -p logs

run_chain() {
  local gpu="$1"
  shift
  local names=("$@")
  echo "GPU ${gpu}: starting chain (${#names[@]} jobs)"
  local name
  for name in "${names[@]}"; do
    echo "[$(date '+%H:%M:%S')] GPU ${gpu}: ${name}..."
    CUDA_VISIBLE_DEVICES="${gpu}" "${CLASSIFY}" "${name}" > "logs/qwen_${name}.log" 2>&1
    echo "[$(date '+%H:%M:%S')] GPU ${gpu}: finished ${name}"
  done
  echo "GPU ${gpu}: chain done"
}

echo "Starting light Qwen chains (sequential per GPU)"
run_chain 0 SEC-bench mmlu &
pid0=$!
run_chain 1 cybersoceval CyberMetric &
pid1=$!
wait "${pid0}" "${pid1}"
echo "All light Qwen jobs finished."
