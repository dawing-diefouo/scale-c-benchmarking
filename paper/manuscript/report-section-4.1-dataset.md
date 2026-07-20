# Section 4.1 — Benchmark Dataset Overview

## 4.1 Benchmark Dataset Overview

Section 3 explained how the evaluation set is built. Here we report the concrete Phase 1 counts that sit behind every accuracy in this chapter. These numbers replace the provisional snapshot mentioned in Section 3.2.

After classification and gold-answer filtering (Sections 3.4–3.5), the NLI-labeled pool contains **897** classified items, of which **573** are scorable. The embedding-labeled pool contains **1,579** classified items, of which **847** are scorable. Those two denominators are what Table 4.2 uses for every fully completed run.

The pools are not the same set of items. Because each classifier assigns topics independently, the mix of topics—and how many items land in each topic—differs. That is why we report two parallel views rather than a single merged ranking.

Of the 573 NLI-scorable items, 322 are marked multiple-choice in the source metadata and 251 are typed as open explanation but still ship with A–D options and a gold letter. Both kinds are scored by exact match. The embedding view follows the same pattern (549 + 298 = 847). Sources that remain in the broader classified pool but contribute no Tier 1 gold answers—mainly JSONSchemaBench, superGLEBer, SEC-bench, and parts of CyberBench—are kept for later structured-output and localization work; they are not discarded.

**Table 4.1 – Phase 1 evaluation pools (scorable Tier 1)**

| Dimension                                 | NLI-classified | Embedding-classified |
| ----------------------------------------- | -------------: | -------------------: |
| Classified items available for evaluation |            897 |                1,579 |
| Scorable items (Table 4.2 denominator)    |            573 |                  847 |
| Leaf topics covered (of 37)               |             32 |                   37 |
| Parent codes covered (of 28)              |             27 |                   28 |
| Course groups covered (of 8)              |              8 |                    8 |
| English / German (scorable)               |       487 / 86 |            644 / 203 |

**Table 4.1a – Scorable items by benchmark family**

| Benchmark family                                            |           NLI |     Embedding |
| ----------------------------------------------------------- | ------------: | ------------: |
| CyberMetric                                                 |           251 |           298 |
| CyberSOCEval (incl. threat-intelligence and malware splits) |           146 |           126 |
| Global-MMLU                                                 |            86 |           316 |
| MMLU (computer security / college computer science)         |            90 |           107 |
| **Total**                                                   |       **573** |         **847** |

**Table 4.1b – Scorable items by course group**

| Course group                      |       NLI (n) | Embedding (n) |
| --------------------------------- | ------------: | ------------: |
| Fundamentals and governance       |           124 |           132 |
| Human and social threats          |            84 |           177 |
| Defensive controls and hygiene    |            77 |           112 |
| Network and secure communications |            77 |            76 |
| Malware and advanced threats      |            72 |           112 |
| Identity and access               |            61 |            82 |
| Applications and workplace        |            48 |           132 |
| Other                             |            30 |            24 |
| **Total**                         |       **573** |         **847** |

Coverage across the eight course groups is complete, but support at the leaf level is uneven. Under NLI labeling, five topics have no scorable items (USB safety, friend requests, unique logins, default usernames, typos). The embedding view covers all 37 leaves, yet unique logins (n = 2) and USB safety (n = 5) are still too thin for reliable topic claims. Further sparse cells are handled as described in Section 4.4.

One modeling caveat affects the denominators directly. Llama 3.3 70B Instruct was scored on a later, topic-capped build rather than the shared 573 / 847 pools, and its NLI run stopped at 327 scorable items. BaronLLM v2 is also short by a few items (569 / 573 NLI; 837 / 847 embedding) after transient API failures. These exceptions are footnoted under Table 4.2 and taken up again in Section 5.4. Until the 70B pair is re-evaluated on the same frozen item set, its deltas should not be over-interpreted.
