# Qwen35 research-source observations on M4 Max

All 12 frozen requests passed prompt/stream validation. The ten held-out requests generated 4,712 retokenized visible tokens: **75.239 visible tokens/s** and **46.812 tokens per total request wall second**, including prompt processing. Total held-out request time was 100.66 seconds. Downloads continued. No submitted source was truncated.

The pinned Unsloth Qwen3.6 35B-A3B UD-Q4_K_M artifact used 32K context, FP16 KV, Metal, reasoning/MTP off, greedy seed 42 and a 1,024 MiB RAM prompt cache. Peak sampled RSS was 24.97 GB (23.26 GiB); sampled system swap remained zero.

## Source fidelity

Codex-assisted review found **18 correct extraction answers and two partial**, with all four source-absent questions correctly answered by abstention. H3-Q3 omits the sons’ removal of Romanus; H4-Q2 omits the two claimants’ uncle/brother relationships. All four stated H3 answers omit the required supporting quotations despite providing page references.

The merged synthesis is exactly the concatenation of the four direct summaries after whitespace normalization. It preserves their errors: H1 reverses who initially held whom at bay; H4 attributes Ottoman reunification to Murad II rather than Mohammed. Other issues include lost qualifications, an unsupported exclusion of systemic failure in the Thessalonica raid, and an unmarked ruler-numeral change from the supplied OCR. The full-source control introduces pre-entry starvation and Valens’s confidence without source support, and supplies no page citations.

The independent full-source summary fully covers **four** compound units, partially covers **nine**, and omits **three**. `review.json` retains every extraction answer, grouped source-linked claims for all six summaries, and all 48 applicable coverage judgments. Eleven distinct factual/qualification error families have 19 manifestations; these annotation counts are not a standardized claim-precision rate. Citation defects and ambiguity are separate.

Normalized prose counts are 204, 186, 223 and 241 words for H1–H4 against 180–220 requested; merged synthesis is 854 words and full-source control 545 against 350–450. Neither synthesis meets its requested length.

This configuration exceeds the requested 40-token speed threshold on both measured rates, but source checking remains necessary. Review measures fidelity to the supplied Oman OCR, not general historical truth, and has no independent human adjudication.

## Evidence

Requests, outputs, settings, memory samples and visible-token receipts are retained. Stream events and large offload excerpts are losslessly gzip-compressed for GitHub; decompress them before using the existing collector/retokenizer. Generation completion and quality review are separate receipts.
