> Historical snapshot. Read the corrected [current report](README.md), [revised counts](error-comparison.md), and [withdrawn-flag record](audits/audit-revisions.json) for current conclusions. Earlier status and judgments below are preserved as history.

# Evo X3 history benchmark: interim results

Updated 8 September 2026, approximately 05:19 UTC / 13:19 Hong Kong.

**No tested configuration has yet met both requirements: at least 35 generated tokens/s and faithful research summaries.** Reasoning-enabled follow-ups are running. This is not a final keep/return recommendation.

## Original configurations: reasoning off

| Configuration | Completed source generation, tokens/s | Completed source pages | Complete final summary | Fidelity finding |
|---|---:|---:|---|---|
| Qwen3.6 35B A3B UD-Q4_K_M, bundled MTP | 55.54–59.62 | 396/396 | No | Critical source-summary errors; final exceeded every bounded output allowance |
| Gemma4 26B A4B IT UD-Q4_K_M | 37.60–38.67 | 396/396 | Yes | Failed the source-grounded full-book audit |
| Qwen3.8 Flash Next IQ4_XS | 22.16–23.36 | 100/396 | No | Source and synthesis errors; second group synthesis exhausted bounded retries |

Rates above cover completed source-summary requests. They exclude controls, capped attempts, and final synthesis. They are generation rates, not elapsed reading or summarization speed. Gemma’s accepted final generated at 40.49 tokens/s.

Flash ran at an 8,192-token context. Its larger tested full-GPU context requests were blocked by the loader’s guardrail. This is a limitation of the tested configuration and workflow, not proof that the hardware cannot support another configuration.

## Time and incomplete work

| Configuration | Book requests, including capped and superseded attempts | Capped requests | Request wall time | Book phase wall time |
|---|---:|---:|---:|---:|
| Qwen3.6 | 19 | 11 | 965.47 s | 1,006.15 s |
| Gemma4 | 10 | 1 | 499.41 s | 519.15 s |
| Flash | 20 | 11 | 1,347.73 s | 1,468.22 s |

Phase totals include loading, token preflight, inference, retries, and intermediate writes. They exclude acquisition, source audits, and gaps between execution phases. Failed workflows cannot be compared as completed-book turnaround times.

Qwen’s final summary hit allowances of 1,800, 3,600, and 7,200 output tokens. Its final retry remained incomplete. Flash first exhausted source-output retries. A bounded adaptive repair completed those source requests, but its second group synthesis still exceeded every permitted allowance. All attempts remain in the evidence.

## Fidelity evidence

Gemma’s completed final received reviewer scores of 2/4 for factual accuracy, chronology and causation, attribution, citations, and coverage. Uncertainty scored 1/4. Passing requires at least 3/4 in every dimension, with no critical unsupported claim, major reversal, or fabricated citation. These are reviewer judgments, not validated accuracy percentages.

The Gemma audit checks 86 final claim units and 24 section-level samples. Major defects include a reversed explanation of Gothic and Vandal weakness, an overstated Nika casualty claim, and false claims that supplied parts of Justinian’s reign were absent.

Qwen’s source summaries confuse Gallienus’s soldiers with Gothic raiders, merge the elder and younger Heraclius, assign Leontius the wrong exile, and reverse the outcome at Durazzo. Its incomplete final does not receive a completed-summary fidelity score.

Flash’s first-group synthesis preserves an obsolete warning that the capital selection is incomplete, despite including the continuation. It also reverses Constantine’s stated concern about Diocletian’s memory.

- [Matched first 50-page comparison](audits/first50-matched-spotcheck.md)
- [Flash completion failure and fidelity review](audits/flash-review.md)
- [Gemma final claim ledger](audits/gemma-final-claims.csv)
- [Gemma review and scoring rationale](audits/gemma-review.md)
- [Gemma section checks](audits/gemma-section-checks.csv)
- [Qwen first-section checks](audits/qwen-first-section.csv)
- [Qwen later section checks](audits/qwen-section-checks.csv)
- [Qwen completion and fidelity review](audits/qwen-review.md)

The matched first-section sample favors Gemma. It does not overturn Gemma’s full-book failure. Legitimate warnings about partial excerpts are distinguished from false absence claims after synthesis.

## Early reasoning-enabled Qwen result

The first completed 50-page section produced visible text at 83.66 tokens/s, but the first visible token took 102.00 seconds. Visible output over the entire accepted request was 8.77 tokens/s. This section contains serious source errors, including AD 196 changed to 1996 and preface claims cited to library-stamp pages. The full-book run continues.

[First reasoning-enabled section audit and timing](audits/qwen-thinking-first-section.md)

## Autonomous follow-ups

The Evo queue has advanced to Qwen with reasoning enabled. Streaming events confirm actual reasoning output. Gemma with reasoning enabled follows, then isolated GPT-OSS120B MXFP4 download, verification, and full-book testing.

A separate Gemma 2 9B Instruct Q4_K_M installation waits until measured runs finish. It adds no new benchmark.

The queue runs under enabled Evo user services with lingering enabled. Closing SSH or shutting down the Mac does not stop it. The Evo must remain powered and connected. Source audits and the final assessment require Codex to resume.

[Persisted queue, configurations, checksums, and status locations](../evo/README.md)

Reasoning-inclusive generation, visible output, first visible token, and full wall time are recorded separately. No speed result from one configuration can be combined with another configuration’s fidelity.

## Source and method

The book is Charles Oman’s *The Byzantine Empire*. The scan has an 1892 copyright and a visually verified 1908 title-page imprint. It contains 396 physical PDF pages. The model input includes all extracted pages, grouped into seven 50-page sections and one 46-page section, with smaller subchunks where required.

[Internet Archive source](https://archive.org/details/byzantineempire00omanrich)

The extracted title-page text omits the 1908 imprint. Models should not be penalized for failing to notice that unsupplied date. Copyright and publication still require distinct treatment.

Physical PDF markers provide citation coordinates. Extraction includes targeted OCR, but maps and illustrations are not fully interpreted. This is a test of the supplied text pipeline, not complete visual reading. Historical statements are checked against Oman; the audit does not silently replace his dates or interpretations with modern knowledge.

The original runs use identical accepted prompts, temperature zero, reasoning off, sequential inference, and actual-token context checks. Output retries and Flash’s bounded adaptive repair are preserved and disclosed. All measured original requests stayed within their actual context limits, with one inference process observed.

[Exact benchmark instructions and rubric](benchmark-instructions.md)

## Memory and operating conditions

| Book-phase peak | Qwen3.6 | Gemma4 | Flash |
|---|---:|---:|---:|
| CPU-visible memory used, GiB | 11.86 | 12.62 | 7.97 |
| Largest runtime RSS, GiB | 7.92 | 8.92 | 4.83 |
| Runtime PSS, GiB | 8.25 | 9.32 | 5.11 |
| GPU VRAM counter, GiB | 24.30 | 19.31 | 63.30 |
| GPU GTT counter, GiB | 0.33 | 0.24 | 0.24 |
| Swap used, GiB | 3.75 | 3.58 | 3.94 |

These counters overlap on unified memory and must not be added. Swap was already in use before testing. Loader-reported model memory and GPU counters use different accounting.

The Evo uses Ryzen AI MAX+ 395, Radeon 8060S, Ubuntu 26.04, and LM Studio’s Vulkan runtime. The CPU-visible allocation is approximately 30.47 GiB, with 96 GiB reserved for the GPU. No BIOS, driver, or power-profile changes were made during the comparison. Load timings are filesystem-cache uncontrolled.

## Web interface

The authenticated private interface is available at [Evo Open WebUI](http://<PRIVATE_HOST>:3000/). The user confirmed access. Account signup is disabled after account creation. Services run independently of the Mac.
