#!/usr/bin/env bash
# Download sknow-lab/Qwen2.5-14B-CIC-ACLARC once into the HF hub cache.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

MODEL="sknow-lab/Qwen2.5-14B-CIC-ACLARC"

echo "Downloading ${MODEL} (one-time HF cache fetch)..."
.venv/bin/python - <<'PY'
from huggingface_hub import snapshot_download

model_id = "sknow-lab/Qwen2.5-14B-CIC-ACLARC"
path = snapshot_download(model_id)
print(f"Cached at: {path}")
PY

echo "Model ready."
