# Mac source-fidelity accuracy results

Both speed and accuracy are measured. See the [complete accuracy scoreboard](scoreboard.md) for every artifact’s current state and the [matched speed comparison](../matched-speed-comparison.md) for repeated synthetic throughput. Pending models have no inferred accuracy score.

The [frozen protocol](../../../../experiments/history-v2-mac/README.md) supplies four passages, 20 extraction questions including four source-absent items, four direct summaries, synthesis from those summaries and an independent full-source control. Two development requests are excluded from scores. **Evaluator: Codex (GPT-6), AI-assisted source adjudication, without independent human review.** This measures fidelity to the supplied Charles Oman OCR, not modern historical truth or general model accuracy. One generation per request/configuration is retained.

## Extraction, citations and quotations

A correct answer can have an incorrect page citation. Partial answers receive no numeric weight. The source-absent items are included in 20 and shown separately out of 4 in the scoreboard. Complete answers include their supporting quotations. Explicit-quotation counts measure marking, not guaranteed verbatim fidelity; reordered or altered quotations are noted in individual reviews.

| Artifact / source ledger | Correct | Partial | Contradiction | Other categories | Fully supported citations /16 | Explicit quotations /16 |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| [qwen3-8b](qwen3-8b/adjudication.json) | 18 | 1 | 1 | 0 | 13 | 4 |
| [nemotron-49b](nemotron-49b/adjudication.json) | 17 | 2 | 1 | 0 | 13 | 12 |
| [gemma4-26b](gemma4-26b/adjudication.json) | 18 | 2 | 0 | 0 | 16 | 16 |
| [qwen36-35b](qwen36-35b/adjudication.json) | 18 | 2 | 0 | 0 | 16 | 12 |
| [qwen38-27b](qwen38-27b/adjudication.json) | 19 | 1 | 0 | 0 | 15 | 16 |
| [qwen35-122b-iq2xxs](qwen35-122b-iq2xxs/adjudication.json) | 17 | 2 | 0 | unsupported: 1 | 15 | 11 |
| [evo-gemma26](evo-gemma26/adjudication.json) | 17 | 3 | 0 | 0 | 16 | 16 |
| [evo-qwen35-mtp-off](evo-qwen35-mtp-off/adjudication.json) | 18 | 2 | 0 | 0 | 16 | 6 |
| [evo-gemma31](evo-gemma31/adjudication.json) | 19 | 0 | 1 | 0 | 15 | 14 |
| [evo-qwen38-27b](evo-qwen38-27b/adjudication.json) | 18 | 2 | 0 | 0 | 16 | 15 |
| [evo-qwen35-community](evo-qwen35-community/adjudication.json) | 18 | 2 | 0 | 0 | 15 | 9 |
| [evo-gemma12-qat](evo-gemma12-qat/adjudication.json) | 19 | 1 | 0 | 0 | 15 | 16 |
| [evo-ministral14](evo-ministral14/adjudication.json) | 18 | 1 | 1 | 0 | 13 | 16 |
| [evo-gemma12-coding](evo-gemma12-coding/adjudication.json) | 17 | 1 | 1 | qualification_loss: 1 | 13 | 16 |
| [evo-gemma2-9b](evo-gemma2-9b/adjudication.json) | 18 | 1 | 1 | 0 | 12 | 1 |

The ledgers retain each answer, source pages, citation category, quotation form and rationale. In the common Mac completeness convention, H3-Q3 requires both removal stages and H4-Q2 requires the uncle/brother relationships. An added unsupported detail or lost numeric bound can change a judgment even when the requested name is correct. A quotation can supply a qualifier missing from the answer’s first sentence. These conventions are stated to make the judgments reviewable.

Development outputs receive separate `development-review.json` files with source judgments and output hashes. They remain excluded from held-out counts. Reviews of completed stages from failed configurations stay with the diagnostic evidence; an incomplete run receives no full-battery score.

## Summary coverage and claim flags

Coverage has 16 predeclared compound units. A unit can be covered even when a represented claim is wrong; the claim ledger records that separately. Omissions, ambiguous wording, citation drift and clear claim errors are distinct. Error families link a direct error to its propagation or independent recurrence. Counts are not standardized atomic-claim precision rates and should not be ranked as such.

| Artifact | Four direct summaries: covered / partial / omitted | Merged: covered / partial / omitted | Full source: covered / partial / omitted | Unique clear families | Manifestations |
| --- | --- | --- | --- | ---: | ---: |
| qwen3-8b | 5 / 10 / 1 | 5 / 10 / 1 | 3 / 9 / 4 | 13 | 21 |
| nemotron-49b | 7 / 8 / 1 | 4 / 10 / 2 | 2 / 9 / 5 | 10 | 12 |
| gemma4-26b | 6 / 8 / 2 | 6 / 8 / 2 | 4 / 5 / 7 | 4 | 5 |
| qwen36-35b | 7 / 8 / 1 | 7 / 8 / 1 | 3 / 10 / 3 | 9 | 20 |
| qwen38-27b | 10 / 5 / 1 | 10 / 5 / 1 | 4 / 2 / 10 | 6 | 14 |
| qwen35-122b-iq2xxs | 8 / 8 / 0 | 8 / 8 / 0 | 5 / 3 / 8 | 14 | 23 |
| evo-gemma26 | 4 / 12 / 0 | 4 / 12 / 0 | 3 / 4 / 9 | 3 | 4 |
| evo-qwen35-mtp-off | 7 / 8 / 1 | 7 / 8 / 1 | 6 / 7 / 3 | 11 | 23 |
| evo-gemma31 | 6 / 10 / 0 | 6 / 10 / 0 | 4 / 4 / 8 | 1 | 2 |
| evo-qwen38-27b | 8 / 7 / 1 | 8 / 7 / 1 | 4 / 5 / 7 | 8 | 15 |
| evo-qwen35-community | 9 / 6 / 1 | 9 / 6 / 1 | 5 / 9 / 2 | 13 | 23 |
| evo-gemma12-qat | 5 / 9 / 2 | 5 / 9 / 2 | 2 / 5 / 9 | 9 | 16 |
| evo-ministral14 | 8 / 7 / 1 | 8 / 7 / 1 | 1 / 11 / 4 | 15 | 25 |
| evo-gemma12-coding | 3 / 12 / 1 | 3 / 12 / 1 | 3 / 5 / 8 | 6 | 10 |
| evo-gemma2-9b | 5 / 10 / 1 | 5 / 10 / 1 | Not submitted | 12 | 23 |

Extraction scores alone do not show whether a model preserves the source in a longer response. Read each ledger’s synthesis review for propagated errors and lost coverage. A short or prematurely self-ended control can omit whole passages without reaching its output cap; that remains an observed omission, not a context exclusion. Context-excluded stages were never submitted and receive no omission score.

## Length and application timing

Normalized prose words remove PDF citation groups, numeric parenthetical references, Markdown styling and punctuation-only tokens before counting whitespace-separated tokens containing letters or numbers. This declared format metric differs from raw whitespace counts, which are also retained. Numeric parentheses can be ambiguous; manual citation review remains necessary. Page references expressed in prose remain in the prose count.

| Artifact | H1 words | H2 words | H3 words | H4 words | Merged words | Full-source words | Full-source first content delta / total seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [qwen3-8b](qwen3-8b/request-metrics.csv) | 278 | 295 | 215 | 290 | 1086 | 591 | 24.29 / 50.08 |
| [nemotron-49b](nemotron-49b/request-metrics.csv) | 221 | 305 | 215 | 234 | 469 | 468 | 100.95 / 197.37 |
| [gemma4-26b](gemma4-26b/request-metrics.csv) | 182 | 173 | 184 | 214 | 723 | 524 | 15.86 / 33.50 |
| [qwen36-35b](qwen36-35b/request-metrics.csv) | 203 | 207 | 219 | 239 | 868 | 474 | 14.67 / 32.77 |
| [qwen38-27b](qwen38-27b/request-metrics.csv) | 227 | 289 | 267 | 264 | 1038 | 529 | 47.71 / 104.09 |
| [qwen35-122b-iq2xxs](qwen35-122b-iq2xxs/request-metrics.csv) | 278 | 229 | 220 | 259 | 830 | 515 | 32.76 / 62.10 |
| [evo-gemma26](evo-gemma26/request-metrics.csv) | 208 | 165 | 183 | 187 | 718 | 418 | 12.18 / 24.88 |
| [evo-qwen35-mtp-off](evo-qwen35-mtp-off/request-metrics.csv) | 220 | 189 | 228 | 241 | 878 | 587 | 11.75 / 30.76 |
| [evo-gemma31](evo-gemma31/request-metrics.csv) | 171 | 166 | 169 | 197 | 661 | 345 | 62.81 / 117.32 |
| [evo-qwen38-27b](evo-qwen38-27b/request-metrics.csv) | 229 | 289 | 262 | 243 | 1019 | 479 | 46.37 / 96.07 |
| [evo-qwen35-community](evo-qwen35-community/request-metrics.csv) | 247 | 203 | 242 | 264 | 1021 | 504 | 12.01 / 22.56 |
| [evo-gemma12-qat](evo-gemma12-qat/request-metrics.csv) | 210 | 160 | 210 | 194 | 770 | 474 | 23.21 / 48.82 |
| [evo-ministral14](evo-ministral14/request-metrics.csv) | 456 | 277 | 211 | 356 | 1302 | 335 | 30.34 / 51.87 |
| [evo-gemma12-coding](evo-gemma12-coding/request-metrics.csv) | 165 | 156 | 162 | 156 | 599 | 364 | 29.60 / 54.68 |
| [evo-gemma2-9b](evo-gemma2-9b/request-metrics.csv) | 234 | 271 | 267 | 299 | 1074 | — | — |

Requested lengths are 180–220 words per direct summary and 350–450 per synthesis/control. Length compliance is not factual accuracy. Application timing includes prompt processing, actual response length and common-prefix cache reuse; model downloads may continue. It is separate from the matched synthetic speed measurements, whose inference intervals suspend this workspace’s download/hash workers. Per-request CSVs include token counts, first nonempty content delta (including whitespace), total time and server decode throughput. The legacy field name is first_visible_seconds; it need not be the first readable word.

## Visible output speed and the 40-token target

The user’s target is above 40 visible generated tokens per second. The following rates retokenize exact assembled output bytes with the same GGUF vocabulary using the pinned [vocabulary-only tokenizer](https://github.com/ggml-org/llama.cpp/blob/050dde50c/tools/tokenize/tokenize.cpp). No model generation is repeated. BOS/EOS insertion, special-token parsing and escape conversion are disabled. Counts include visible formatting whitespace and exclude API-only reasoning/control tokens.

Visible-phase rate is total retokenized tokens divided by the sum of last-minus-first nonempty content-delta intervals. It is a stream-boundary estimate, includes the first delta in the numerator and can include network scheduling; the first delta can be whitespace. First readable-delta delays are also retained in each CSV. Request-wall rate divides by the sum of generation-request wall times, including prompt processing and completion. It excludes server startup, preflight tokenization calls and pauses between requests. These measures differ from synthetic throughput, server prediction time and Evo’s SDK method. Development requests are excluded from this table.

| Artifact / evidence | Submitted held-out requests | Visible-phase tokens/s | Tokens / request wall second | Above 40 in visible phase |
| --- | ---: | ---: | ---: | --- |
| [qwen3-8b](qwen3-8b/visible-speed.csv) | 10 | 38.79 | 26.51 | No |
| [nemotron-49b](nemotron-49b/visible-speed.csv) | 10 | 7.34 | 5.10 | No |
| [gemma4-26b](gemma4-26b/visible-speed.csv) | 10 | 49.94 | 33.47 | Yes |
| [qwen36-35b](qwen36-35b/visible-speed.csv) | 10 | 46.94 | 33.75 | Yes |
| [qwen38-27b](qwen38-27b/visible-speed.csv) | 10 | 14.13 | 10.28 | No |
| [qwen35-122b-iq2xxs](qwen35-122b-iq2xxs/visible-speed.csv) | 10 | 29.98 | 19.03 | No |
| [evo-gemma26](evo-gemma26/visible-speed.csv) | 10 | 57.52 | 39.57 | Yes |
| [evo-qwen35-mtp-off](evo-qwen35-mtp-off/visible-speed.csv) | 10 | 58.36 | 41.69 | Yes |
| [evo-gemma31](evo-gemma31/visible-speed.csv) | 10 | 12.48 | 8.05 | No |
| [evo-qwen38-27b](evo-qwen38-27b/visible-speed.csv) | 10 | 14.25 | 10.34 | No |
| [evo-qwen35-community](evo-qwen35-community/visible-speed.csv) | 10 | 70.26 | 46.81 | Yes |
| [evo-gemma12-qat](evo-gemma12-qat/visible-speed.csv) | 10 | 32.00 | 21.85 | No |
| [evo-ministral14](evo-ministral14/visible-speed.csv) | 10 | 28.36 | 21.20 | No |
| [evo-gemma12-coding](evo-gemma12-coding/visible-speed.csv) | 10 | 24.44 | 15.63 | No |
| [evo-gemma2-9b](evo-gemma2-9b/visible-speed.csv) | 9 | 34.85 | 26.33 | No |

Passing the speed target is not an accuracy pass. Actual outputs, citation failures, omissions, context exclusions and word-limit compliance remain separate. These are one-battery application observations, without repeated-battery uncertainty estimates.

## Evidence and interpretation

Each model directory retains exact requests, timestamped raw stream data events, assembled outputs, finish reasons, observed runtime sampling/speculation settings, memory samples and full-offload evidence. The generator verifies completion of the stream; collection independently reconstructs payloads from frozen fixtures, checks hashes and stream/output agreement, and confirms observed settings. Gold never enters the model requests. Source judgments are separate files and are not generated by the metric collector.

Falcon 180B Chat’s supported 2048-token context cannot fit this complete battery plus the output allowance. It receives separate speed/capacity/coherence checks. Gemma2 uses 8192 tokens and explicitly excludes only stages whose complete prompts cannot fit. Other load or memory failures are reported as failures, never fabricated accuracy scores.

The published Arc and Evo ledgers use some different completeness conventions and configurations. Unadjusted counts do not establish cross-computer accuracy differences. Exact weight matches support the speed comparison; they do not remove differences in context, templates, reasoning/MTP settings, outputs or evaluator conventions.
