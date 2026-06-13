---
dataset_info:
  features:
  - name: question
    dtype: string
  - name: options
    list: string
  - name: answers
    list: string
  - name: topic
    dtype: string
  - name: difficulty
    dtype: string
  - name: report_id
    dtype: string
  - name: attack
    dtype: string
  splits:
  - name: malware_analysis
    num_bytes: 259686
    num_examples: 609
  - name: threat_intel_reasoning
    num_bytes: 380164
    num_examples: 588
  download_size: 241844
  dataset_size: 639850
configs:
- config_name: default
  data_files:
  - split: malware_analysis
    path: data/malware_analysis-*
  - split: threat_intel_reasoning
    path: data/threat_intel_reasoning-*
license: mit
language:
- en
tags:
- cybersecurity
---

# CyberSOCEval Questions

These datasets were originally only available on [GitHub](https://github.com/meta-llama/PurpleLlama/tree/main/CybersecurityBenchmarks/datasets/crwd_meta) under MIT license. I have ported them to Hugging Face without modification. Each benchmark has its own split: `malware_analysis` and `threat_intel_reasoning`.
