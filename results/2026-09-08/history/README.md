# Evo X3 original history-summary experiment

The original workflow exposed source-fidelity and completion problems across the tested configurations. These findings concern one book, its prompts, runtime settings, and synthesis pipeline. They do not establish general unsuitability for supervised historical research.

The original performance threshold was at least 35 generated tokens per second. The later preference is above 40 visible tokens per second. Native generation, visible-phase speed, and whole-request waiting time remain separate. No configuration passed the original provisional fidelity rubric alongside its speed requirement.

## Completed workload and scope

| Configuration | Source pages completed | Accepted final | Measured speed scope | Audit outcome |
| --- | ---: | --- | --- | --- |
| Qwen3.6 35B UD-Q4_K_M, MTP, reasoning OFF | 396/396 | No | Completed source requests: 55.54–59.62 native tokens/s | Source errors; final exhausted bounded retries |
| Gemma4 26B A4B UD-Q4_K_M, reasoning OFF | 396/396 | Yes | Completed source requests: 37.60–38.67 native tokens/s | 14 material flags across 86 final units |
| Qwen3.8 Flash Next IQ4_XS, reasoning OFF | 100/396 | No | Completed source subrequests: 22.16–23.36 native tokens/s | Incomplete workflow and below original speed threshold |
| Qwen3.6 35B UD-Q4_K_M, MTP, reasoning ON | 396/396 | Yes | All book attempts: 69.85–81.08 native tokens/s | 69 material flags across 113 final units |
| Gemma4 26B A4B UD-Q4_K_M, reasoning ON | 396/396 | Yes | All book attempts: 38.81–41.79 native tokens/s | 18 material flags across 87 final units |
| GPT-OSS120 MXFP4, template-medium | 396/396 | Yes | Completed source requests: 41.20–43.31 visible-phase tokens/s | 75 material flags across 151 final units |

Speed scopes differ explicitly. These are not matched synthetic timings or architecture-only comparisons. The [separate speed package](../evo/README.md) supplies matched llama-bench results.

Flags count output units, including citation defects. They are not independent error families or calibrated accuracy percentages. Final lengths and unit counts differ substantially. Targeted section checks investigate suspicious claims and cannot estimate general error rates. Do not add section and final counts.

## Reasoning and waiting time

| Measure | Qwen ON | Gemma ON | GPT template-medium |
| --- | ---: | ---: | ---: |
| Book phase, including loading/preflight | 28.83 min | 57.40 min | 24.77 min |
| Total request wall time | 28.50 min | 56.89 min | 21.08 min |
| Total generated tokens | 105,173 | 125,779 | 36,843 |
| Reasoning tokens | 93,047 | 116,874 | 15,471 |
| Retokenized visible tokens | 12,093 | 8,846 | 21,272 |
| Visible tokens / total request wall second | 7.07 | 2.59 | 16.82 |
| Requests / capped attempts | 13/4 | 13/4 | 10/1 |
| Accepted-final first-visible delay | 125.08 s | 558.38 s | 13.05 s |
| Accepted-final request wall time | 157.23 s | 594.36 s | 193.50 s |

The wall totals retain retries and empty visible responses. Native generation includes reasoning tokens and excludes prompt processing. Visible-phase rates begin at the first visible fragment and include final-response overhead. They should not be confused with visible tokens divided by total waiting time.

GPT’s accepted-final native TTFT was 0.117 seconds after a cached retry prefix. Its first visible answer still arrived after 13.05 seconds. The accepted final contained 7,983 retokenized visible tokens and 5,288 words including citations, against a 900-word request. Qwen ON’s final contained 1,744 words including citations, or 1,404 excluding them. Gemma ON’s final contained 799 including citations, or 786 excluding them.

## Source-grounded findings

Gemma OFF’s final applied the six-day Nika casualty estimate to the Hippodrome assault. It also reversed the source’s explanation of Gothic weakness into Roman failure. Its final limitations paragraph invented whole-book omissions from local chunk boundaries.

Two earlier Gemma OFF objections were withdrawn after closer review. The source explicitly acknowledges missing details of Leo’s reforms. A war beginning in 540 can overlap a plague beginning in 542. The corrected total is 14 material flags, not 16. The [revision record](audits/audit-revisions.json) and [worked examples](audits/gemma-errors-explained.md) preserve these corrections.

Qwen ON changed AD 196 to 1996 and confused the two Heraclius figures. Its final described the 1453 conquest, then falsely claimed the supplied book ended before 1204. Citations repeatedly pointed to front matter or unrelated periods.

Gemma ON repeated the Nika casualty-scope error and removed the 328/329 uncertainty. It also misdated Theodoric’s completed conquest and reversed the object of officials’ extortion. These findings concern particular output statements, not every use of the model.

GPT’s final changed the end of a Persian war into the end of Justinian’s reign. It assigned Burtzes’s disobedience to Phocas. It also converted a statement about Janissary backgrounds into a territorial statistic. Its long accepted answer omitted the substantive ending despite all source groups entering synthesis.

The [error comparison](error-comparison.md) links every completed final ledger. All judgments were made through Codex-assisted comparison with supplied source text. They are not independent human adjudication. The user reviewed selected examples, not the complete ledger.

## Source and reproducibility

Charles Oman’s *The Byzantine Empire* supplies 396 physical PDF pages. The scan is a 1908 printing of an 1892 work. Its PDF SHA-256 is `0187c4b558c683d5349b4cf427db4ca9713298f0e99660767d8dfbc2aa83c5f2`. The canonical extraction preserves OCR noise and source inconsistencies. Its title image’s 1908 imprint did not enter model text and was not scored as missing knowledge.

Eight nominal groups cover seven 50-page spans and a final 46-page span. The final request synthesizes intermediate summaries. The same book and core prompts were used, while context capacity, MTP, samplers, reasoning, and output budgets differed. Flash required smaller subrequests and stopped after 100 pages. Its loader guardrail does not establish a universal hardware capacity limit.

GPT initially received two rejected API configurations, retained in the record. Native `top_k=0` and `reasoning=medium` were unsupported. Corrected requests omit both fields. Top-k remains server-default and uncontrolled; medium was verified in the template. Qwen’s recommended presence penalty was unavailable and was not applied.

Original files, retries, accepted outputs, caps, and exact configurations are retained. [Raw runs](raw/runs/) preserve numerical records and source-based text. [Canonical pages](source/pages.json) allow exact input reconstruction. Archived scripts preserve historical logic; public-path redactions and refreshed file hashes are disclosed. Portable history helpers are separate from the new [frozen accuracy pilot](../../../experiments/history-v2/USAGE.md).

## Practical interpretation

This demanding full-book pipeline did not meet its provisional rubric. That does not make these models categorically unusable for research. Bounded extraction, explicit abstention, source verification, and human review can support different workflows. The new pilot separates extraction, direct summaries, merged summaries, and full-source controls to identify where errors arise.

No maximum hardware-performance claim follows from these results. The balanced-profile speed baseline, later reversible tuning checks, and source-fidelity assessments should remain separately labeled.
