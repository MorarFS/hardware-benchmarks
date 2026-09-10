# Qwen27 research-source observations on M4 Max

All 12 frozen requests passed prompt/stream validation. Ten held-out requests generated 5,499 retokenized visible tokens: **14.885 visible tokens/s** and **9.025 tokens per total request wall second**, including prompt processing. Total held-out request time was 609.32 seconds. The full-source prompt contained 13,916 tokens and was not truncated. Downloads continued.

The pinned Unsloth Qwen3.8 27B UD-Q4_K_M artifact used 32K context, FP16 KV, Metal, reasoning/MTP off, greedy seed 42 and a 1,024 MiB RAM prompt cache. Peak sampled RSS was 22.24 GB (20.71 GiB); sampled system swap remained zero.

## Source fidelity

Codex-assisted review found **19 correct extraction answers and one partial**, including correct abstention on all four source-absent questions. Qwen27 correctly preserved both succession stages in H3-Q3. H4-Q2 still omits the claimants’ uncle/brother relationships. H2-Q4 quotes across pages 174–175 but cites only 174.

The stronger extraction result does not extend to reliable synthesis. The full-source control fully covers **four** compound units, partially covers **one**, and omits **eleven**. It drops the entire H4 excerpt, the Christian social-history topics in H2, and even H1’s Adrianople outcome. It stops naturally after 763 API completion tokens, below the 2,048 cap; these omissions are not caused by input truncation or reaching that cap.

Direct summaries introduce an unsupported location for the initial Hunnic invasion, lose the Latin estimate’s probability and upper bound, and add an unsupported regnal numeral to Mohammed. The merged synthesis largely copies the direct summaries and repeats those defects. The full-source control independently repeats the Hunnic-location error and probability loss.

All direct summaries exceed the requested 180–220 words: 227, 283, 267 and 264 normalized prose words. The merged output is 1,032 words and full-source control 529 against 350–450. Full-source citations use prose locators rather than the requested bracket syntax; several individual locators also need correction.

The ledger in `review.json` contains all 20 extraction rows, all 48 applicable coverage judgments and grouped claims for all six summaries. Six factual/qualification error families have 14 manifestations; these counts are not standardized claim precision. Ambiguous readings, citation defects and coverage remain separate. Review measures fidelity to the supplied Oman OCR, with no independent human adjudication.

This configuration misses the 40-token research target on both measured rates. Its single-battery extraction advantage should not be treated as an overall quality ranking.

## Evidence

Exact requests, outputs, settings, memory observations and retokenization receipts are retained. Stream events and large offload excerpts are losslessly gzip-compressed for GitHub; decompress before running the original collector/retokenizer. Generation completion and quality review are separate receipts.
