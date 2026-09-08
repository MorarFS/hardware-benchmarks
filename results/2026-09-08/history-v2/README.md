# Frozen history-v2 accuracy results

Focused extraction largely preserved the supplied facts. Summary generation still lost coverage and introduced errors. These findings concern one frozen pilot, not general historical-research suitability.

All 36 requests completed, without output caps or inference errors. The workload contained 12 requests per model, including two development requests. The source audit covers 60 held-out answers and 18 summary outputs. Generation finished on 8 September 2026 at 12:47 UTC.

## Fixed questions and justified abstention

| Configuration | Fully supported answers, of 16 answerable | Partial | False abstention | Correct abstention, of 4 absent |
| --- | ---: | ---: | ---: | ---: |
| Gemma26, reasoning OFF | 14 | 2 | 0 | 4 |
| Qwen35, reasoning OFF, MTP ON | 15 | 1 | 0 | 4 |
| GPT-OSS120, template-medium | 15 | 0 | 1 | 4 |

Gemma incompletely explained the food policy’s causal contribution to revolt. Gemma and Qwen omitted the first stage of Romanus’s removal. Both correctly described the subsequent expulsion of his sons.

GPT incorrectly declined that same succession question, H3-Q3. PDF243 explicitly describes both removals. This is a missed answer, not invented information.

All four absent-answer cases were checked against their complete supplied passages. Adrianople’s casualty figures do not answer the separate Ad Salices question. Numbers of monks do not establish numbers of monasteries. A rescue reward does not establish annual cavalry pay. Later population and mercenary totals do not establish siege casualties.

The [60-row extraction ledger](extraction-ledger.csv) preserves answers, references, and judgments. Quotation fidelity remains separate from answer meaning. Qwen omitted six requested quotations; GPT omitted one and altered two. Alternative brackets, nonbreaking hyphens, and terminal periods were not scored as factual errors.

## What changed during summarization

| Configuration | Direct-summary findings | Merged-summary behavior | Independent full-source control |
| --- | --- | --- | --- |
| Gemma26 OFF | Latin extinction overstatement; citation drift; incomplete coverage | Inherits earlier defects; drops another paganism qualification | Omits H2 and H4 entirely; misattributes a quoted Gothic historian |
| Qwen35 OFF/MTP | Names Murad as Ottoman reunifier, contradicting the supplied Mohammed account | Repeats all four direct summaries, unchanged after whitespace normalization | Repeats wrong reunifier; invents cross-period contemporaneity and “last emperor” status |
| GPT-OSS120 medium | Changes gladiatorial location and agency; misstates kinship; makes counterfactual rescue factual | Retains all four factual-error families | Makes a reported vision the siege’s sole saving cause; narrows surviving Latin enclaves incorrectly |

Qwen answered the reunifier extraction question correctly before misidentifying him in its summary. The same underlying information can survive extraction but fail during composition.

GPT locates abolished gladiatorial games in Constantinople. PDF171 says Constantinople never knew those games; the surviving games were at Rome. It also combines state measures with Telemachus’s separate individual action. These are two error families within one compound statement.

GPT calls Constantine Leo’s grandson, although he was Leo’s son. The source identifies them as Basil’s son and grandson. GPT also converts a hypothetical rescue into a successful recapture. PDF242 instead says the attackers departed with their booty.

Gemma’s “vanished” loses the source’s surviving Latin speakers and qualified decline. Such scope changes remain distinct from clear actor or event contradictions. Missing explicit attribution to Oman is not automatically fabricated historical information.

Qwen silently substitutes John VIII for the source’s John VI. This violates source fidelity, rather than establishing falsehood against modern historical scholarship. The audit does not silently correct Oman using outside knowledge.

The [issue ledger](issue-ledger.csv) records exact spans, source pages, and explanations. Its 31 manifestations include qualification, attribution, and citation defects. They are not 31 independent false facts. The [precision notes](precision-notes.json) separately preserve ambiguity and smaller locator problems.

Merged outputs received summaries, so repeated defects can be classified as inherited. Full-source controls received original passages. Their repeated errors are independent recurrence, not propagation.

## Coverage and instruction following

Each passage has four frozen, compound coverage units. “Covered” requires its specified components; “partial” records missing components. Presence does not imply factual correctness. These counts are descriptive, not calibrated accuracy scores.

| Configuration | Four direct summaries: covered / partial / omitted | Merged: covered / partial / omitted | Full-source: covered / partial / omitted |
| --- | --- | --- | --- |
| Gemma26 OFF | 5 / 10 / 1 | 5 / 9 / 2 | 4 / 3 / 9 |
| Qwen35 OFF/MTP | 7 / 9 / 0 | 7 / 9 / 0 | 3 / 12 / 1 |
| GPT-OSS120 medium | 7 / 7 / 2 | 7 / 7 / 2 | 4 / 7 / 5 |

The [144-row coverage ledger](coverage-ledger.csv) identifies every missing component. Naming Fritigern is required for full coverage of H1’s first unit. Merely mentioning the Visigoths therefore receives partial credit under this frozen criterion.

| Configuration | Direct prose words: H1 / H2 / H3 / H4 | Merged prose words | Full-source prose words |
| --- | --- | ---: | ---: |
| Gemma26 OFF | 226 / 175 / 194 / 183 | 699 | 432 |
| Qwen35 OFF/MTP | 223 / 195 / 207 / 235 | 860 | 477 |
| GPT-OSS120 medium | 204 / 419 / 237 / 310 | 1,170 | 601 |

Direct summaries requested 180–220 words. Both synthesis conditions requested 350–450 words. Counts remove citation markers and Markdown formatting, then count whitespace-separated words containing letters or numbers. Hyphenated forms remain single words. Raw whitespace counts are also retained.

All merged outputs exceeded their requested length. Qwen’s merged output exactly concatenates the four direct summaries after whitespace normalization. Gemma’s control meets the length range but omits two passages. Its four paragraphs cover H1 three times, then H3 once.

Qwen’s control combines H2 and H3 within one paragraph. GPT keeps one paragraph per passage, but reduces H2 to Latin’s decline. Its labels incorrectly narrow H1 to PDF61–66 and H2 to PDF169–170.

All controls use parenthesized page numbers. This is shorthand rather than the direct-summary prompt’s explicit PDF-marker syntax. It remains possible to recover their physical-page references. GPT also uses em dashes despite the style instruction. See [instruction checks](instruction-checks.csv).

## Speed and waiting time

| Configuration | Visible-phase range, all 12 requests | First visible answer range | Total request wall time |
| --- | ---: | ---: | ---: |
| Gemma26 OFF | 42.54–46.63 tokens/s | 4.38–17.29 s | 192.52 s |
| Qwen35 OFF/MTP | 61.65–95.96 tokens/s | 3.69–18.04 s | 140.96 s |
| GPT-OSS120 medium | 44.70–49.19 tokens/s | 9.87–78.50 s | 427.84 s |

Visible-phase rates exclude waiting before the first visible fragment. They include final-response overhead. Total request wall time includes prompt processing and reasoning, but excludes model loading.

GPT generated 9,124 reasoning tokens across these requests. Gemma and Qwen generated none. Qwen’s fastest visible rate occurred during verbatim synthesis. That rate does not demonstrate useful compression or improved accuracy.

These application measurements differ from the matched synthetic speed matrix. MTP, prompts, output lengths, and reasoning differ between configurations. Request-level numbers appear in [request metrics](request-metrics.csv).

## Method and reproducibility

The frozen suite uses four discontinuous passages, approximately 1,900–2,300 words each. Their physical PDF ranges are 61–67, 169–176, 241–247, and 358–367. Development used PDF101–106. Held-out means excluded from prompt development, not prior book exposure or model training.

All 17 frozen fixture hashes remain unchanged. Gold answers were not supplied to generation requests. The original prompts, reference answers, coverage units, and configuration profiles remain in the [published suite](../../../experiments/history-v2/USAGE.md).

The Evo used Vulkan, full GPU placement, F16 K/V caches, and seed 42. Context was 65,536 tokens, with one parallel session. Evaluation batch size was 2,048; physical batch size was 512. An SDK load wrapper enforced settings omitted from native CLI metadata. Actual-load records verify these settings; Qwen’s native record also verifies MTP and three draft tokens.

GPT’s template contains medium reasoning. The native API rejected explicit medium and top-k zero fields earlier. Those fields remain omitted; top-k is consequently uncontrolled. The portable runner documents operator-side load verification separately. The archived deployment script preserves Evo-specific orchestration with private-path placeholders. It is evidence, not a portable entry point.

Three startup/preflight failures preceded the successful generation. They involved serving readiness and verification of default cache/seed settings. Their archived files contain no held-out generation outputs. All successful requests, configurations, streams, telemetry, and terminal evidence appear under [raw records](raw/). Earlier failed attempts remain under [startup attempts](raw/accuracy-v2-attempts/).

The review used Codex-assisted comparison against complete supplied text. Another Codex task checked source references, all absence cases, and selected judgments. It also checked all GPT extraction answers. Neither review constitutes independent human adjudication or PDF-image verification.

The [review decisions](review-decisions.json) preserve conservative revisions and evaluator identity. The [citation-segment ledger](citation-segment-ledger.csv) covers all 18 summary outputs. Its 290 segments can contain multiple claims or sentence fragments. They must not become an atomic-claim denominator or overall accuracy percentage.

The table builder performs bookkeeping, not factual evaluation. Run it from the repository root:

~~~sh
python results/2026-09-08/history-v2/build_audit_tables.py --raw results/2026-09-08/history-v2/raw/accuracy-v2-results --suite experiments/history-v2 --decisions results/2026-09-08/history-v2/review-decisions.json --output work/rebuilt-history-v2
~~~

Private paths and host identifiers are redacted in public copies. Original metadata hashes refer to original files; the public manifest hashes sanitized files. Model answers and numerical measurements retain their original content.

## Practical interpretation

This pilot supports bounded, source-checked extraction as a promising workflow. It does not establish that prompting alone caused improvement over the original experiment. The tasks, budgets, and evidence structure changed together.

All three models still require review when producing connected historical summaries. Gemma’s fewer clear factual contradictions coexist with substantial coverage loss. Larger or longer answers did not reliably preserve the supplied evidence. No general model ranking follows from one run across four passages.
