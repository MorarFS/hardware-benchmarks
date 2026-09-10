# Gemma26 research-source observations on M4 Max

All 12 frozen requests completed and passed prompt/stream validation. The ten held-out requests generated 4,649 retokenized visible tokens: **85.456 visible tokens/s** and **48.918 tokens per total request wall second**, including prompt processing. Total held-out request time was 95.04 seconds. The full-source prompt had 13,773 tokens and was not truncated. Downloads continued.

This exact bartowski Q4_K_M artifact used 32K context, FP16 KV, one Metal slot, reasoning/MTP off, greedy seed 42 and a 1,024 MiB RAM prompt cache. Peak sampled RSS was 20.89 GB (19.45 GiB); sampled system swap remained zero. Runtime allocations and RSS are not independent memory pools to add together.

## Source review

Codex-assisted review, without independent human adjudication: **18 correct extraction answers and two partial answers**, including correct abstention on all four absent-answer questions. H3-Q3 omits the first succession stage; H4-Q2 omits the claimants’ uncle/brother relationships. Quote length, page references and format compliance are separate from those answer categories.

The summaries still contain errors. H3 says Romanus kept Constantine in the background until majority, whereas the source explicitly says long after majority. H2 drops the author’s probability qualifier on the AD 400 Latin-speaker estimate. Both recur in the merged synthesis. H1 cites the casualty passage on PDF 66 rather than 67.

The full-source control covers **six compound units completely, seven partially, and omits three** under the strict documented rubric. It loses most of H4’s causal sequence and merges the four excerpts into an uneven structure. It also switches to printed book pages 340/341 at the end instead of physical PDF 366/367. `review.json` contains every coverage judgment and selected error anchors; the selected errors are not an exhaustive claim annotation.

| Output | Prose words | Requested range | Citation observation |
|---|---:|---:|---|
| H1 direct summary |187|180–220|11 PDF markers|
| H2 direct summary |176|180–220|8 PDF markers|
| H3 direct summary |189|180–220|10 PDF markers|
| H4 direct summary |198|180–220|10 PDF markers|
| Merged synthesis |738|350–450|39 PDF markers; repeats some parent errors|
| Full-source control |625|350–450|28 parenthetical numeric markers, no requested PDF-marker syntax|

This is a promising measured speed result for supervised source work. It is not an overall research-quality winner: omissions, chronology and citation errors remain. The small selected OCR suite does not establish general historical accuracy.

## Evidence

All requests, outputs, settings, memory samples and visible-token receipts are retained. Stream events and the large offload excerpt are gzip-compressed in GitHub storage; decompress them before using the existing collector/retokenizer. Generation completion and source review remain separate receipts.
