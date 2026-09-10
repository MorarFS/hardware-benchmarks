# Flash-Next mixed Q2/Q4: frozen source battery

All 12 requests finished naturally: two development requests and ten held-out requests. The full-source input contained 13,916 tokenized tokens. Configuration: greedy sampling, seed 42, thinking disabled through the chat template, 2,048 output-token cap, fresh native cache per request, no KV quantization, 256-token prefill chunks, complete disk-backed PLE, and target-only decoding without MTP. The explicit Sawfwair normalization compatibility helper was active.

The ten held-out requests produced 5,255 visible tokens over 164.1763 visible-phase seconds and 315.9054 request-wall seconds: **32.0083 visible tokens/s** and **16.6347 tokens/wall second**. Startup and work between requests are excluded. Retained stream/output identity and exact frozen prompts were independently reconstructed by `validate-m4-flash-next.py`.

Extraction: **18 correct and 2 partial**, with the four source-absent questions included in 20 total. H3-Q3 omits that Romanus’s sons forced his abdication; H4-Q2 omits the uncle/brother relationships. All four absent answers are correct. H1–H3 omit the required supporting quotations for their 12 stated answers; H4 supplies quotations. Formatting and citations are separate from factual correctness.

Direct-summary word counts are 273, 222, 244, and 286 against 180–220 requested. The merged response copies all four direct summaries after whitespace normalization, totaling 1,025 words instead of 350–450. Its errors propagate unchanged, including Constantine wrongly described as Leo’s grandson and lost qualifications concerning Latin, administrative change and paganism.

The full-source control writes 784 words in four paragraphs, all about H1’s opening narrative. It stops normally after 1,036 generated tokens, below the 2,048 cap. Coverage is **2 complete, 0 partial, 14 omitted**: all H2–H4 material is missing, as are H1’s later battles and the defensive ending. Its paragraph-end `(pp.N–N)` locators also fail the requested per-sentence physical-PDF citation form. Later context diagnostics retrieve material from other parts of the same source, so a simple input-truncation explanation is not supported.

Peak MLX allocation: 41.7855 GB. Peak sampled RSS: 28,152,463,360 bytes. Do not add these counters. Sampled global swap remains at the pre-existing approximately 123 KiB throughout this battery. The later separate context diagnostic does incur swap growth and is documented separately.

`adjudication.json` retains 20 extraction judgments, 48 coverage judgments, 192 grouped claim annotations, eight error families and 17 manifestations. These grouped annotations are not standardized atomic units or a precision denominator. Review concerns fidelity to the supplied Oman OCR rather than modern historical truth and is AI-assisted without independent human adjudication.
