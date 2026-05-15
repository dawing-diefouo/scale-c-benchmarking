---
task_categories:
- token-classification
- summarization
- multiple-choice
- text-classification
language:
- en
size_categories:
- 10K<n<100K
---
# CyberBench: A Multi-Task Cybersecurity Benchmark for LLMs

## Introduction

CyberBench is a comprehensive multi-task benchmark specifically designed to evaluate the capabilities of Large Language Models (LLMs) in the cybersecurity domain. It includes ten diverse datasets that span tasks such as Named Entity Recognition (NER), Summarization (SUM), Multiple Choice (MC), and Text Classification (TC). By providing this specialized benchmark, CyberBench facilitates a systematic evaluation of LLMs in cybersecurity, helping to identify their strengths and areas for improvement. For more details, refer to the [GitHub repository](https://github.com/jpmorganchase/CyberBench) or the [AICS'24 paper](http://aics.site/AICS2024/AICS_CyberBench.pdf).

## Benchmark Overview

| **Task**                 | **Dataset**   | **Data Size** | **Input**                   | **Output**                  | **Metric**        | **License**                                   |
|--------------------------|---------------|---------------|-----------------------------|-----------------------------|-------------------|-----------------------------------------------|
| **NER**                 | [CyNER](https://github.com/aiforsec/CyNER)    | 4,017         | Sentence                   | Entities                   | Micro F1        | [MIT](https://github.com/aiforsec/CyNER/blob/main/LICENSE.txt)  |
|                         | [APTNER](https://github.com/wangxuren/APTNER)   | 9,971         | Sentence                   | Entities                   | Micro F1        | [Fair Use](https://github.com/wangxuren/APTNER/blob/main/README.md)     |
| **Summarization**       | [CyNews](https://github.com/cypher-07/Cybersecurity-News-Article-Dataset)   | 3,742         | Article                    | Headline                   | ROUGE-1/2/L     | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| **Multiple Choice**     | [SecMMLU](https://github.com/hendrycks/test)  | 116           | Question and Choices       | Answer                     | Accuracy         | [MIT](https://github.com/hendrycks/test/blob/master/LICENSE)  |
|                         | [CyQuiz](https://github.com/Ebazhanov/linkedin-skill-assessments-quizzes)   | 128           | Question and Choices       | Answer                     | Accuracy         | [AGPL-3.0](https://github.com/Ebazhanov/linkedin-skill-assessments-quizzes/blob/main/LICENSE) |
| **Text Classification** | [MITRE](https://github.com/mitre/cti)  | 10,873        | Procedure Description       | Technique ID and Name      | Accuracy         | [MITRE Terms of Use](https://attack.mitre.org/resources/legal-and-branding/terms-of-use/) |
|                         | [CVE](https://www.kaggle.com/datasets/krooz0/cve-and-cwe-mapping-dataset)      | 14,652        | CVE Description            | Severity                   | Accuracy         | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) |
|                         | [Web](https://www.kaggle.com/datasets/shashwatwork/web-page-phishing-detection-dataset)      | 11,429        | URL                        | Phishing/Legitimate        | Binary F1        | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
|                         | [Email](https://www.kaggle.com/datasets/subhajournal/phishingemails)    | 13,281        | Email Text                 | Phishing/Safe              | Binary F1        | [GNU LGPL](https://www.gnu.org/licenses/lgpl-3.0.html) |
|                         | [HTTP](https://github.com/msudol/Web-Application-Attack-Datasets)     | 12,213        | HTTP Request               | Anomalous/Normal           | Binary F1        | [GPL-3.0](https://github.com/msudol/Web-Application-Attack-Datasets/blob/master/LICENSE) |

## License Information

Each dataset in CyberBench follows its original licensing terms. This repository aggregates the datasets for benchmarking purposes and adheres to the respective licenses of the datasets included. Details for each license can be found in the links above.

## Citation

If you find CyberBench useful in your research, please cite our paper:

```bibtex
@misc{liu2024cyberbench,
  title={Cyberbench: A multi-task benchmark for evaluating large language models in cybersecurity},
  author={Liu, Zefang and Shi, Jialei and Buford, John F},
  howpublished={AAAI-24 Workshop on Artificial Intelligence for Cyber Security (AICS)},
  year={2024}
}
```