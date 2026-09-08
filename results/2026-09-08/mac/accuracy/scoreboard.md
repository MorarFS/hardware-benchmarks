# Mac history accuracy scoreboard

Codex (GPT-6), AI-assisted source review; no independent human adjudication. Same frozen source tasks and acceptable variants. Counts measure fidelity to supplied OCR, not modern historical truth or general accuracy. Citation support and quotation compliance are separate. Source-absent items are included in the 20-question denominator and also shown out of 4. Partial answers are not assigned a numeric weight.

| Artifact ID | Correct /20 | Partial /20 | Contradiction /20 | Other /20 | Correct absent /4 | Full-source coverage: covered / partial / omitted | State |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| qwen3-8b | 18 | 1 | 1 | 0 | 4 | 3 / 9 / 4 | source adjudicated |
| nemotron-49b | 17 | 2 | 1 | 0 | 4 | 2 / 9 / 5 | source adjudicated |
| gemma4-26b | 18 | 2 | 0 | 0 | 4 | 4 / 5 / 7 | source adjudicated |
| qwen36-35b | 18 | 2 | 0 | 0 | 4 | 3 / 10 / 3 | source adjudicated |
| qwen38-27b | 19 | 1 | 0 | 0 | 4 | 4 / 2 / 10 | source adjudicated |
| qwen35-122b-iq2xxs | 17 | 2 | 0 | 1 | 4 | 5 / 3 / 8 | source adjudicated |
| falcon180b-chat-iq1s | — | — | — | — | — | — | context exclusion: supported 2048 cannot contain complete frozen passages and output |
| evo-gemma26 | 17 | 3 | 0 | 0 | 4 | 3 / 4 / 9 | source adjudicated |
| evo-qwen35-mtp-off | 18 | 2 | 0 | 0 | 4 | 6 / 7 / 3 | source adjudicated |
| evo-gemma31 | 19 | 0 | 1 | 0 | 4 | 4 / 4 / 8 | source adjudicated |
| evo-qwen38-27b | 18 | 2 | 0 | 0 | 4 | 4 / 5 / 7 | source adjudicated |
| evo-qwen35-community | 18 | 2 | 0 | 0 | 4 | 5 / 9 / 2 | source adjudicated |
| evo-gemma12-qat | 19 | 1 | 0 | 0 | 4 | 2 / 5 / 9 | source adjudicated |
| evo-ministral14 | 18 | 1 | 1 | 0 | 4 | 1 / 11 / 4 | source adjudicated; output cap reached |
| evo-gemma12-coding | 17 | 1 | 1 | 1 | 4 | 3 / 5 / 8 | source adjudicated |
| evo-gemma2-9b | 18 | 1 | 1 | 0 | 3 | — | source adjudicated; partial battery |

All three count columns for coverage total 16 units when that stage is adjudicated. A context-excluded control must not receive 16 omissions: it was not submitted. Pending generation/review is not an accuracy score. See model directories for exact requests, outputs, telemetry, source anchors and separate citation findings.

The published Arc and Evo ledgers use some different completeness conventions and configurations. Their unadjusted counts must not be interpreted as calibrated cross-computer accuracy differences. Cross-machine weight matches are documented in the speed table; histories also differ in context and some original MTP/reasoning settings.
