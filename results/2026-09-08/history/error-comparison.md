# Model error comparison

Updated 8 September 2026. GPT final audit is complete.

No tested configuration has passed both speed and source fidelity. GPT has the largest raw material-flag count: 75 across 151 final claim units. Qwen reasoning ON follows with 69 across 113 units. GPT also wrote a much longer answer. These findings do not establish a general accuracy ranking.

## Fully audited completed final summaries

| Model | Reasoning | Reviewed claim units | Critical | Major | Moderate | Material flagged units |
|---|---|---:|---:|---:|---:|---:|
| Gemma 4 26 B | OFF | 86 | 2 | 3 | 9 | 14 |
| Qwen 3.6 35 B | ON | 113 | 4 | 41 | 24 | 69 |
| Gemma 4 26 B | ON | 87 | 0 | 10 | 8 | 18 |
| GPT-OSS 120 B | medium | 151 | 17 | 29 | 29 | 75 |

Counts describe output claim units, including citation errors. They are not independent error families or accuracy percentages. Output length and claim selection differ. Minor wording and locator issues are omitted from this table. Some ledger units contain multiple related defects.

Qwen OFF exhausted its final-output retries. Flash stopped after two source groups. Neither has a completed final for this table. GPT completed its final retry, but omitted the substantive ending and failed fidelity.

## Targeted source checks

| Model | Reasoning | Checked units | Critical | Major | Moderate |
|---|---|---:|---:|---:|---:|
| Qwen 3.6 35 B | OFF | 39 | 2 | 8 | 15 |
| Qwen 3.6 35 B | ON | 35 | 4 | 16 | 10 |
| Gemma 4 26 B | OFF | 24 | 0 | 1 | 2 |
| Gemma 4 26 B | ON | 24 | 1 | 8 | 3 |
| GPT-OSS 120 B | medium | 43 | 13 | 16 | 6 |

These samples deliberately investigate suspicious claims. They are not random samples or comparable error rates. All source groups were sampled, except Flash’s incomplete pipeline. The [matched first-section review](audits/first50-matched-spotcheck.md) covers three original configurations. Gemma handled those particular passages best.

## Concrete errors and source locations

| Configuration | Output error | Source correction | Physical PDF pages | Severity |
|---|---|---|---|---|
| Qwen OFF | Gothic raiders nearly exterminated the original population. | Oman attributes that destruction to Gallienus’s soldiers, with qualification. | 36 | Critical |
| Qwen ON | AD 196 becomes “nineteen hundred and ninety-six.” | The source dates the siege to AD 196. | 35 | Critical |
| Qwen ON | The book ends before the Fourth Crusade. | The supplied text continues through 1453. | 300–376 | Critical |
| Gemma ON | Theodoric conquered Italy in 488. | That date concerns his offer and departure. | 90 | Major |
| Gemma ON | The Hippodrome massacre killed 35,000. | Oman qualifies that estimate and covers six days of disturbances. | 106 | Major |
| GPT medium | Justinian’s reign ended in 532. | The sentence concerns the first Persian war. | 101 | Critical |
| GPT medium | Phocas stormed Antioch against orders. | Burtzes disobeyed Phocas. | 257 | Critical |
| GPT medium | The empire shrank to two-thirds of its earlier size. | The statistic concerns Grand Viziers’ Janissary backgrounds. | 350–351 | Critical |
| Flash OFF | Constantine wished to avoid eclipsing Diocletian’s memory. | Constantine feared Diocletian’s memory would eclipse his own. | 43 | Major causal reversal |

## Propagation versus distinct errors

Qwen’s date corruption appears in both its first section and final synthesis. Count this as one underlying error family across stages. Its false ending warning also propagates from a partial section. Repeated faulty front-matter citations affect many final claims but share citation-mapping failures.

The tables count manifestations within each audited stage. Do not add source and final counts. Distinct-error-family totals have not been exhaustively deduplicated. Raw ledgers preserve claim IDs and source evidence for verification.

Source fidelity follows the supplied Oman text, including its own historical mistakes. Contradictory source dates and OCR uncertainty require explicit qualification. The extracted title page omitted the 1908 imprint; models did not receive that date.

GPT’s [completed review](audits/gptoss-review.md) and [151-unit final ledger](audits/gptoss-final-claims.csv) provide full details.

## Evidence

- [gemma-final-claims.csv](audits/gemma-final-claims.csv)
- [gemma-section-checks.csv](audits/gemma-section-checks.csv)
- [gemma-thinking-final-claims.csv](audits/gemma-thinking-final-claims.csv)
- [gemma-thinking-section-checks.csv](audits/gemma-thinking-section-checks.csv)
- [gptoss-section-checks.csv](audits/gptoss-section-checks.csv)
- [qwen-first-section.csv](audits/qwen-first-section.csv)
- [qwen-section-checks.csv](audits/qwen-section-checks.csv)
- [qwen-thinking-final-claims.csv](audits/qwen-thinking-final-claims.csv)
- [qwen-thinking-first-section.csv](audits/qwen-thinking-first-section.csv)
- [qwen-thinking-section-checks.csv](audits/qwen-thinking-section-checks.csv)

Audit revision: two Gemma OFF flags were withdrawn after closer source review. Leo’s missing reform details are source-supported. “Simultaneously” permits overlapping events. The prior material count was 16; the revised count is 14. See [revision record](audits/audit-revisions.json).
