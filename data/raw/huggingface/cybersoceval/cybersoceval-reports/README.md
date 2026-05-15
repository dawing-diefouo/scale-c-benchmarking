---
dataset_info:
  features:
  - name: id
    dtype: string
  - name: url
    dtype: string
  - name: source
    dtype: string
  - name: report
    dtype: string
  splits:
  - name: malware_analysis
    num_bytes: 30632814
    num_examples: 175
  - name: threat_intel_reasoning
    num_bytes: 1629625
    num_examples: 45
  download_size: 6005381
  dataset_size: 32262439
configs:
- config_name: default
  data_files:
  - split: malware_analysis
    path: data/malware_analysis-*
  - split: threat_intel_reasoning
    path: data/threat_intel_reasoning-*
license:
- cc-by-nd-4.0
- cc-by-sa-4.0
---

# CyberSOCEval Reports

These datasets were originally only available on [GitHub](https://github.com/CrowdStrike/CyberSOCEval_data). Each benchmark has its own split: `malware_analysis` and `threat_intel_reasoning`. Instead of including original URLs or PDF files for the `threat_intel_reasoning` reports, I converted each report to markdown using [Qwen3-VL-30B-A3B-Thinking](https://huggingface.co/Qwen/Qwen3-VL-30B-A3B-Thinking) and manually reviewed the outputs before including them in this dataset.

## Licenses

The original source contains data from multiple sources, each with its own licensing terms:

- malware_analysis - [Creative Commons Attribution ShareAlike 4.0 International (CC BY-SA 4.0)](https://github.com/CrowdStrike/CyberSOCEval_data/blob/main/data/hybrid-analysis/LICENSE.md)
- threat_intel_reasoning - [Creative Commons Attribution No Derivatives 4.0 International (CC BY-ND 4.0)](https://github.com/CrowdStrike/CyberSOCEval_data/blob/main/data/crowdstrike-reports/LICENSE.md)
