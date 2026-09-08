# Historical research with local models: findings and prompting lessons

The Evo runs these models at useful generation speeds. Source fidelity still depends on the task, prompt, and verification workflow. The strongest result came from bounded extraction, not unrestricted historical synthesis.

## What the accuracy pilot found

Twenty fixed questions included four genuinely absent answers. Gemma26 produced 18 correct responses, including all four justified abstentions. Its remaining two answers were incomplete. Qwen35 produced 19 correct responses and one incomplete answer. GPT-OSS120 produced 19 correct responses and one false abstention.

GPT’s missed answer concerned the removal of Romanus Lecapenus and his sons. The supplied page explicitly describes both stages. Allowing abstention helps, but refusals still require checking.

Gemma had no confirmed hard factual contradiction under this pilot’s reviewed categories. It nevertheless lost qualifications, misplaced citations, and omitted important content. Its full-source control omitted two of the four passages entirely.

Qwen and GPT made clear summary errors despite strong extraction results. Qwen correctly identified Mohammed during extraction, then named Murad as reunifier during summarization. GPT changed kinship, misplaced gladiatorial games, and converted a hypothetical rescue into an event.

Qwen’s merged answer repeated all four summaries verbatim after whitespace normalization. All three merged answers exceeded the requested word range. Fluency, length, and fast generation did not establish successful synthesis.

The original full-book experiment found substantive Gemma errors as well. This smaller pilot therefore does not establish that Gemma is generally error-free. These are Codex-assisted source checks, not independent human adjudication or a calibrated ranking. [Detailed pilot results](https://github.com/MorarFS/hardware-benchmarks/blob/main/results/2026-09-08/history-v2/README.md), [original history audit](https://github.com/MorarFS/hardware-benchmarks/blob/main/results/2026-09-08/history/README.md).

## How fast the models were

| Exact weight profile | Matched synthetic generation at depth 2,048 | Original book source requests | New pilot visible-phase range |
| --- | ---: | ---: | ---: |
| Gemma26 A4B UD-Q4_K_M | 47.37 tokens/s | 37.60–38.67 native tokens/s | 42.54–46.63 tokens/s |
| Qwen35 A3B UD-Q4_K_M | 59.60 tokens/s, MTP OFF | 55.54–59.62 native tokens/s, MTP ON | 61.65–95.96 tokens/s, MTP ON |
| GPT-OSS120 MXFP4 | 52.59 tokens/s | 41.20–43.31 visible-phase tokens/s | 44.70–49.19 tokens/s |

Synthetic results use pinned Vulkan b10852, tg256, five repetitions, and speculation OFF. They measure compute throughput without chat prompts or reasoning.

Application rates involve different prompts, outputs, and reasoning settings. Gemma and Qwen used reasoning OFF here; GPT used template-default medium. Qwen’s MTP was ON, separately from thinking. Native rates can include reasoning tokens. Visible-phase rates begin after the first visible output.

The pilot’s first visible answers arrived after 4.38–17.29 seconds for Gemma. Qwen took 3.69–18.04 seconds; GPT took 9.87–78.50 seconds. Qwen’s highest rate accompanied verbatim synthesis, rather than effective compression.

Earlier whole-book trials also enabled reasoning for Gemma and Qwen. Those trials took much longer and still contained source-fidelity errors. They do not prove that thinking always reduces accuracy.

These scopes should remain separate when comparing computers. The original threshold was at least 35 generated tokens per second. The later preference was above 40 visible tokens per second. [Speed evidence](https://github.com/MorarFS/hardware-benchmarks/blob/main/results/2026-09-08/evo/README.md), [Mac reproduction guide](https://github.com/MorarFS/hardware-benchmarks/blob/main/MAC-BENCHMARK.md).

## Proposed workflow for historical work

These refinements follow the observed failures. They are proposals, not experimentally demonstrated repairs.

1. Extract claims before synthesis. Require a short source quotation and physical PDF page.
2. Preserve uncertainty and attribution. Separate Oman’s judgments, reported testimony, and narrated events.
3. Build an actor and chronology list. Distinguish similarly named rulers, relatives, and succession stages.
4. Specify coverage by source section. Check every required component after generation.
5. Keep excerpt limits local. Missing details in one passage do not establish whole-book omissions.
6. Verify citations against actual pages. Nearby pages can discuss related events without supporting the claim.
7. Permit “not stated,” then check abstentions. The model can miss an explicit answer.
8. Require genuine synthesis. Compare merged text against inputs to detect simple concatenation.
9. Check word counts externally. A requested word limit does not enforce itself.
10. Evaluate revisions on separate passages. Develop prompts before examining held-out outputs.
11. Separate source fidelity from historical truth. Flag source inconsistencies before applying outside corrections.
12. Retain human review. Extraction accuracy does not guarantee accurate narrative composition.

A proposed extraction instruction is:

> Use only the supplied passage. Answer each question independently. Give a short supporting quotation and its physical PDF page. Preserve qualifications and reported status. If the answer is absent, write “Not stated in the supplied passage.” Do not infer identities or quantities from unrelated details.

A proposed synthesis instruction is:

> Use the verified claim table and source excerpts. Write one paragraph per source section, in page order. Cover every listed component. Preserve named actors, causal relationships, uncertainty, and attribution. Do not invent links across gaps or repeat the input summaries verbatim. Cite supporting physical PDF pages. Follow the specified word range.

Neither proposed prompt has been tested as a new experiment. Check the resulting text rather than treating these instructions as safeguards that guarantee correctness.

The broader [research notes](https://github.com/MorarFS/hardware-benchmarks/blob/main/RESEARCH-NOTES.md) retain runtime findings and relevant humanities resources. The [frozen test package](https://github.com/MorarFS/hardware-benchmarks/blob/main/experiments/history-v2/USAGE.md) supports reproduction on another machine.
