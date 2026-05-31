# Qwen classification batch runs

Each script classifies all `.jsonl` files under one Hugging Face dataset tree and writes mirrored output to:

```text
data/processed/qwen/<dataset-name>/...
```

Example: `data/raw/huggingface/mmlu/computer_security/test.jsonl` → `data/processed/qwen/mmlu/computer_security/test.jsonl`

## Suggested 4-GPU layout (2 jobs per GPU, ~56 GB VRAM each)

| GPU | Terminal 1 | Terminal 2 |
|-----|------------|------------|
| 0 | `./scripts/batch/classify_qwen_cyberbench.sh` | `./scripts/batch/classify_qwen_CyberMetric.sh` |
| 1 | `./scripts/batch/classify_qwen_cybersoceval.sh` | `./scripts/batch/classify_qwen_SEC-bench.sh` |
| 2 | `./scripts/batch/classify_qwen_mmlu.sh` | `./scripts/batch/classify_qwen_Global-MMLU.sh` |
| 3 | `./scripts/batch/classify_qwen_JSONSchemaBench.sh` | `./scripts/batch/classify_qwen_superGLEBer.sh` |

Override the GPU per run:

```bash
CUDA_VISIBLE_DEVICES=2 ./scripts/batch/classify_qwen_mmlu.sh
```

## Launch all 8 at once (background)

```bash
mkdir -p logs
CUDA_VISIBLE_DEVICES=0 ./scripts/batch/classify_qwen_cyberbench.sh > logs/qwen_cyberbench.log 2>&1 &
CUDA_VISIBLE_DEVICES=0 ./scripts/batch/classify_qwen_CyberMetric.sh > logs/qwen_CyberMetric.log 2>&1 &
CUDA_VISIBLE_DEVICES=1 ./scripts/batch/classify_qwen_cybersoceval.sh > logs/qwen_cybersoceval.log 2>&1 &
CUDA_VISIBLE_DEVICES=1 ./scripts/batch/classify_qwen_SEC-bench.sh > logs/qwen_SEC-bench.log 2>&1 &
CUDA_VISIBLE_DEVICES=2 ./scripts/batch/classify_qwen_mmlu.sh > logs/qwen_mmlu.log 2>&1 &
CUDA_VISIBLE_DEVICES=2 ./scripts/batch/classify_qwen_Global-MMLU.sh > logs/qwen_Global-MMLU.log 2>&1 &
CUDA_VISIBLE_DEVICES=3 ./scripts/batch/classify_qwen_JSONSchemaBench.sh > logs/qwen_JSONSchemaBench.log 2>&1 &
CUDA_VISIBLE_DEVICES=3 ./scripts/batch/classify_qwen_superGLEBer.sh > logs/qwen_superGLEBer.log 2>&1 &
wait
```

Each script exports `CUDA_VISIBLE_DEVICES` if not already set; pass it on the command line to override.
