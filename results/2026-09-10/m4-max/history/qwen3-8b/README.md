# Qwen3 8B research-source observations on M4 Max

All 12 frozen requests completed and independently passed payload/stream validation; two development requests are excluded from held-out aggregates. This establishes valid execution, not factual reliability. The model used a 32,768-token context, FP16 KV, Metal, greedy seed 42, reasoning/speculation off and a 1,024 MiB RAM prompt cache. Downloads continued.

The ten held-out requests produced 4,899 retokenized visible tokens: **38.747 tokens/s during the visible phase**, or **21.609 tokens per total request wall second**, including prompt processing. Total held-out request time was 226.71 seconds. The full-source prompt had 13,738 tokens and was not truncated. See `visible-speed.json` and `request-metrics.csv` for boundaries and individual observations.

## Source review

Codex-assisted review, without independent human adjudication: **18 correct extraction answers, one partial answer, one contradiction**; all four source-absent answers correctly abstained, with separate formatting deviations. This is fidelity to supplied Oman OCR, not general historical truth or model accuracy.

- H3-Q3 confuses the two succession stages: the source has Romanus’s sons depose their father, then the mob/guards expel the sons. The response assigns different agents and partly contradicts its own supporting sentence.
- H4-Q2 omits the rival claimants’ uncle/brother relationships.
- H1-Q4 and H4-Q2 give wrong page citations. Several extractions omit marked supporting quotations. Correct abstention does not imply exact-format compliance.

The summaries reveal practical research risks. H2 incorrectly says Johannes Lydus lacked Latin proficiency, although the source says that skill enabled his career. H4 dates Manuel’s death to 1422, although the source places death three years after the 1422 return to vassalage. Both errors propagate into synthesis. Synthesis invents new page-range headings 1–8 instead of retaining physical source pages.

The full-source control also lost substantial coverage: **three complete, nine partial and four omitted** compound units under the documented strict rubric. Its coverage table and selected claim-error anchors are in `review.json`. The selected error examples are not an exhaustive annotation of every summary claim.

| Output | Prose words | Requested range | PDF citation markers |
|---|---:|---:|---:|
| H1 direct summary |309|180–220|0|
| H2 direct summary |295|180–220|0|
| H3 direct summary |215|180–220|0|
| H4 direct summary |290|180–220|5|
| Merged synthesis |1,117|350–450|9, including invented headings|
| Full-source control |591|350–450|0|

Eight of the ten held-out output texts exactly match the prior M5 Pro Qwen8 outputs; H1 summary and merged synthesis differ. Faster synthetic decoding did not remove source errors. This is a specific observed match, not a claim that backend changes always preserve output.

## Evidence and reproduction

`review.json` is separate from immutable generation receipts. JSON records, requests, rendered outputs, observed settings and memory samples are retained. Stream events and the large offload excerpt are gzip-compressed for storage; decompress them before running the existing collector or retokenizer. All uncompressed bytes are preserved by gzip. `complete.json` retains its original pre-review quality-status wording; the later review is explicitly separate.

```sh
# Run in this evidence directory after downloading repository files:
gzip -dk -- *-stream.jsonl.gz offload.txt.gz
# From the repository root, validate and collect a fresh local run:
python3 scripts/history_v2/collect_mac.py qwen3-8b --source local-results/m4-max-history/qwen3-8b --output results/2026-09-10/m4-max/history/qwen3-8b
python3 scripts/history_v2/retokenize_m4.py qwen3-8b
```
