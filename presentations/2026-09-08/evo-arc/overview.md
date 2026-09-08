# Evo X3 and Windows Arc: historical research comparison

8 September 2026. Accessible companion to the six-slide editable presentation.

The Arc was faster in the shared synthetic tests. The Evo ran GPT-OSS 120B. Strong extraction results did not produce consistently reliable summaries. These findings describe tested configurations and one source-bound pilot.

## Slide 2: Speed and model capacity

Evo X3

Ryzen AI MAX+ 395 · Radeon 8060S
Ubuntu 26.04 · Vulkan

96 GiB reserved for the integrated GPU.
Shared memory architecture; not discrete VRAM.

GPT-OSS 120B ran with 63.39 GB weights.

Original baseline: balanced.
Current daily profile: performance.

Windows laptop + external Arc

Ryzen AI 9 365 · about 16 GB system RAM
Arc Pro B70 · 32 GB discrete VRAM · SYCL

Intel Thunderbolt 5 / USB4 dock detected.
Negotiated link bandwidth was not measured.

Internal RTX 5060 Laptop: 8 GB VRAM.

GPT-OSS 120B was not tested on Arc.


**Interpretation and limits.** Do not add the Evo GPU reservation and CPU-visible RAM as independent physical memory pools. The Evo has approximately 30.47 GiB CPU-visible memory after the 96 GiB GPU reservation. Different memory architectures and software stacks prevent a simple memory-for-memory comparison. The Windows machine used AC power. The detected dock is not proof of negotiated bandwidth.

## Slide 3: Arc is faster in the shared synthetic tests

Generation at 2,048-token depth; 256 generated tokens; five repeats. llama-bench b10852, full GPU offload, F16 cache, flash attention. Reasoning and MTP off.

| Model / tested weight family | Evo tokens/s | Arc tokens/s | Comparability |
| --- | --- | --- | --- |
| Qwen3 8B · official Q4_K_M | 40.90 | 72.84 | Strongest match: identical GGUF hash |
| Qwen3.6 35B-A3B · UD Q4 | 59.60 | 71.53 | Artifacts differ; MTP disabled here |
| Gemma 4 26B-A4B · Q4 | 47.37 | 56.68 | Different quantizers |
| Qwen3.8 27B · Q4 | 12.58 | 20.42 | Different artifacts / quantization |
| GPT-OSS 120B · MXFP4 | 52.59 | Not run | Evo capacity result; no Arc comparison |

**Interpretation and limits.** Rates are mean tg256 at depth2048, not prose accuracy or end-to-end throughput. Qwen8 identical official GGUF is the closest hardware comparison; operating systems/backends still differ. Evo Qwen35 here is the UD artifact used in the audit. A separate installed community Qwen35 reached 69.43 tokens/s, so 59.60 is not the fastest installed Evo result. Internal RTX5060 Qwen8 was 62.01 tokens/s. These additional configurations are not silently substituted. The optional Arc Nemotron49B capacity test is outside this table. Evo original baseline was balanced.

## Slide 4: History timings include different kinds of waiting

Twelve requests each; loading excluded. Qwen / Gemma reasoning OFF; GPT-OSS template medium. Evo: visible-phase rates. Arc: server decode rates. Rate definitions differ; do not pool them.

| System / model | Rate: tokens/s | Rate basis | First visible: seconds | Total: seconds |
| --- | --- | --- | --- | --- |
| Evo · Qwen35, MTP on | 61.65–95.96 | Visible phase range | 3.69–18.04 range | 140.96 |
| Evo · Gemma26 | 42.54–46.63 | Visible phase range | 4.38–17.29 range | 192.52 |
| Evo · GPT-OSS120 | 44.70–49.19 | Visible phase range | 9.87–78.50 range | 427.84 |
| Arc · Qwen35, MTP off | 68.39 | Weighted decode | 4.89 median | 139.00 |
| Arc · Gemma26 | 52.20 | Weighted decode | 4.08 median | 156.11 |
| Arc · Qwen27 | 19.94 | Weighted decode | 12.71 median | 490.35 |

**Interpretation and limits.** Evo native LM Studio SDK retokenized visible output. Its visible phase excludes initial waiting but includes final overhead. Arc completion-token counts divided by summed server prediction time include any control tokens in that counter and exclude prompt processing. Evo GPT used template-medium reasoning, generated 9,124 reasoning tokens, and had unsupported native top-k and reasoning fields omitted after preflight. Qwen35 MTP was on for Evo history and off for Arc. Gemma and Qwen artifacts differ across machines. Qwen35 Evo fastest merge output was an exact whitespace-normalized concatenation of direct summaries. Total wall times cover different outputs and lengths, so they are not an isolated hardware comparison. Only one battery per configuration.

## Slide 5: Strong extraction coexists with summary errors

Twenty questions include four true absences. All configurations answered those four correctly. This secondary content crosswalk uses Evo conventions; stricter Arc completeness scores differ.

| System / model | Supported / 20 | Partial | Other answer issue | Summary finding |
| --- | --- | --- | --- | --- |
| Evo · Qwen35 | 19 | 1 | None in this category | Wrong reunifier; merge copies summaries |
| Evo · Gemma26 | 18 | 2 | None in this category | Full-source control omits two passages |
| Evo · GPT-OSS120 | 19 | 0 | 1 false abstention | Kinship, cause and location errors propagate |
| Arc · Qwen35 | 19 | 1 | Duplicated answer ID | Wrong reunifier; merge omits H4 |
| Arc · Gemma26 | 18 | 1 | 1 false-absence claim | Reunification / cession conflation |
| Arc · Qwen27 | 19 | 1 | None in this category | Wrong seller; full-source omits H4 |

**Interpretation and limits.** Small source-bound, Codex/AI-assisted audit, not independent human adjudication or a general accuracy ranking. Four answerable source passages from Charles Oman, The Byzantine Empire. Seventeen fixture hashes were frozen before held-out generation. Partial answers receive no arbitrary half-credit. Arc initial strict completeness counts were Qwen35 16, Gemma16, Qwen27 19. The secondary published crosswalk yields the table shown. ¹Arc Qwen35 repeats H1-Q4; content mapping identifies H1-Q5, while strict ID matching subtracts one supported answer. ²Arc Gemma gives a correct second component but falsely claims Romanus removal is absent; this category differs from Evo GPT declining the whole answer. No claim that Gemma is generally error-free: the original full-book audit found material errors. All six configurations have summary defects. Citation, quotation, coverage and word-limit audits remain separate.

The answer counts combine 16 answerable questions and four true absences. They do not count all historical claims in summaries. Arc Gemma’s false-absence claim appears within a partly correct answer. Evo GPT instead declined the whole answer. These categories differ.

## Slide 6: Model choices for historical work

Start with Qwen35

It combined useful speed with strong extraction content in this pilot.

Every configuration still needs source checks for summaries.

The Mac comparison should preserve frozen prompts and report its own weight hashes.

| Focus | Interpretation |
| --- | --- |
| Daily Evo | Performance mode is saved. Paired checks found no meaningful speed gain. |
| Larger models | Evo fits GPT-OSS120. This pilot established no general quality advantage. |
| Source fidelity | Check claims, qualifiers, citations and coverage separately from speed. |
| Mac replication | Published handoff covers capacity, >40 tokens/s and the shared accuracy suite. |

**Interpretation and limits.** The performance profile was explicitly requested after the reversible comparison and is saved in power-profiles-daemon state; daemon active and enabled. No reboot test was performed. Two-model paired profile comparison had small n, fixed order and no randomized crossover; it does not establish a causal thermal or performance effect. Qwen prose mean changed −1.19%, Gemma +0.63%. Speed alone cannot justify summary trust. Mac hardware is user-reported M5 Pro 48GB and should be verified by the running Mac task. Do not claim Mac results or that the Mac task has read the handoff. Handoff asks to avoid duplicate GPU runs and choose the largest practical historical-research capacity candidate with memory headroom.

## Reproduction and sources

The deck uses native PowerPoint text and three editable tables. It retains the selected Simple Light Mode template. Six slides were rendered and visually inspected. Package, geometry, font-policy and import checks were run. Native PowerPoint execution was not tested.

Source snapshot: `5a99a555753f61f51a50c2089a06831a8b675349`. The published build script imports the template supplied through `TEMPLATE_PPTX`. The source data retains slide text, tables, notes and citations. No inference is needed to rebuild the presentation.

- [MAC-HANDOFF.md (MAC-HANDOFF.md)](https://github.com/MorarFS/hardware-benchmarks/blob/5a99a555753f61f51a50c2089a06831a8b675349/MAC-HANDOFF.md)
- [MODERN-MODELS.md (MODERN-MODELS.md)](https://github.com/MorarFS/hardware-benchmarks/blob/5a99a555753f61f51a50c2089a06831a8b675349/MODERN-MODELS.md)
- [README.md (README.md)](https://github.com/MorarFS/hardware-benchmarks/blob/5a99a555753f61f51a50c2089a06831a8b675349/README.md)
- [README.md (results/2026-09-08/arc-history-v2/README.md)](https://github.com/MorarFS/hardware-benchmarks/blob/5a99a555753f61f51a50c2089a06831a8b675349/results/2026-09-08/arc-history-v2/README.md)
- [README.md (results/2026-09-08/evo/README.md)](https://github.com/MorarFS/hardware-benchmarks/blob/5a99a555753f61f51a50c2089a06831a8b675349/results/2026-09-08/evo/README.md)
- [README.md (results/2026-09-08/history-v2/README.md)](https://github.com/MorarFS/hardware-benchmarks/blob/5a99a555753f61f51a50c2089a06831a8b675349/results/2026-09-08/history-v2/README.md)
- [README.md (results/2026-09-08/power-profiles/README.md)](https://github.com/MorarFS/hardware-benchmarks/blob/5a99a555753f61f51a50c2089a06831a8b675349/results/2026-09-08/power-profiles/README.md)

Mac results are pending and are not included here.
