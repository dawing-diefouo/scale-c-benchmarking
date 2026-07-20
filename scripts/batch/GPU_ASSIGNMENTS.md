# Qwen classification batch runs

Classify one upstream dataset:

```bash
./scripts/batch/classify_qwen.sh CyberMetric
CUDA_VISIBLE_DEVICES=2 ./scripts/batch/classify_qwen.sh mmlu
```

Output mirrors under `data/processed/qwen/<dataset>/...`.

## Dataset sizes (raw row counts)

| Benchmark | Files | Rows | Load |
|-----------|------:|-----:|------|
| SEC-bench | 3 | 305 | light |
| mmlu | 9 | 832 | light |
| cybersoceval | 4 | 1,417 | light |
| CyberMetric | 4 | 12,760 | medium |
| Global-MMLU | 4 | 28,654 | heavy |
| JSONSchemaBench | 48 | 43,402 | heavy |
| cyberbench | 1 | 80,422 | heavy |
| superGLEBer | 82 | 487,191 | heaviest |

## 4-GPU layout

| GPU | Jobs | ~rows |
|-----|------|------:|
| 0 | SEC-bench, mmlu | 1,137 |
| 1 | cybersoceval, CyberMetric | 14,177 |
| 2 | cyberbench, Global-MMLU | 109,076 |
| 3 | JSONSchemaBench, superGLEBer | 530,593 |

## Launch all 8

```bash
./scripts/batch/run_qwen_all.sh --bg
tail -f logs/qwen_*.log
```
