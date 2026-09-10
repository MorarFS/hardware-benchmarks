# Nemotron49 research-source observations on M4 Max

All 12 frozen requests passed independent payload/stream validation at **32K context**, FP16 KV, Metal, greedy seed 42, cache 1024 and the documented native `/no_think` adapter. No reasoning output or source truncation occurred. The full-source prompt used 13,541 tokens. Transfers continued until they finished naturally during this battery; they were never paused.

Ten held-out requests produced 5,329 retokenized visible tokens in 1,026.256 request-wall seconds: **9.268 visible tokens/s** and **5.193 tokens per request-wall second**. Peak sampled process RSS was 39.693 GB (36.97 GiB), with system swap zero throughout sampled snapshots. Unlike the earlier M5 profile, this M4 run completed at 32K; context, cache, machine and concurrent load differ, so this is not an isolated hardware effect.

## Source fidelity

Codex-assisted review: **17 correct extraction answers, two partial, one contradiction**. All four truly source-absent answers correctly abstain. H2-Q4 supplies the causal mechanism but resists the question’s Oman attribution; H4-Q2 omits claimant kinship; H3-Q3 says the passage does not identify who removed Romanus, then describes his sons making him abdicate. Several answers have wrong page references or omit requested supporting quotations.

Full-source coverage is **2 complete / 9 partial / 5 omitted**. Three paragraphs focus on H1, while the other three excerpts share one paragraph. The control invents siege expertise as a reason the Goths failed, treats the planned attack as an actual siege, and overstates the Eastern army’s permanent failure to recover.

The merged synthesis propagates the incorrect Visigothic identity of the Wallachian remnant and an unsupported reconstructed date range. It newly attributes starvation to Valens’s admission conditions, moves cavalry adoption into the war, and changes ongoing Latin decline into completed disappearance. Its explicit attribution of monastic criticism is retained as an improvement over the direct summary, rather than copying the older M5 flag.

All four extraction outputs and the H1/H4 direct summaries exactly match the older M5 outputs. Changed H2/H3, merged and full-source passages were independently checked. `historical-output-comparison.json` records equality, and `adjudication.json` retains 20 extraction rows, 48 coverage judgments and 130 grouped claim annotations. Eleven factual/qualification error families have 13 manifestations; these counts are not standardized claim precision. Citation, ambiguity, coverage and attribution findings remain separate. No independent human adjudication.

Normalized word counts are 221, 314, 223 and 234 for H1–H4 against 180–220 requested; merged synthesis is 541 and the full-source control 470 against 350–450. These counts include heading words after stripping formatting and page markers.

This configuration is below the requested 40-token research target on both observed rates. Transport completion and memory fit do not establish research reliability.

## Evidence

Exact requests, outputs, runtime settings, memory samples and retokenization receipts are retained. Stream events and large offload excerpts are losslessly gzip-compressed for GitHub; decompress before using the existing collector/retokenizer. Full private runtime logs remain local.
