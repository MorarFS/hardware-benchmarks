# Local AI for historical research

Research snapshot: 8 September 2026. Prepared for the Evo X3 benchmark project.

## Purpose and interpretation

The updated target is sustained generation above 40 visible tokens per second. Historical accuracy, source fidelity, and practical waiting time remain separate requirements. The original benchmark used a 35-token threshold; retain that distinction in comparisons.

Matched speed tests and bounded ROCm repair checks are now complete. [The measured Evo results](results/2026-09-08/evo/README.md) remain separate from these external research leads. Fast repetition does not qualify as useful generation. Neither these notes nor one benchmark establishes the machine’s maximum performance.

## Backend distinction

Vulkan and HIP/ROCm provide different GPU execution paths in llama.cpp. Installing ROCm does not accelerate a process using Vulkan. Both can coexist for controlled comparisons using the same model file. [llama.cpp build documentation](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md)

AMD provides inference guidance and binaries for supported Ryzen APUs. An isolated, architecture-compatible runtime provides a useful diagnostic control. Record its release, dependencies, and supported platform. Documentation for AMD Instinct servers does not establish Ryzen compatibility. [AMD AI ecosystem guidance](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/inference/llamacpp.html), [AMD Ryzen inference documentation](https://rocm.docs.amd.com/projects/radeon-ryzen/en/latest/docs/advanced/advancedryz/linux/llm/llm.html)

## ROCm correctness leads

| Primary source | Reported observation | Relevance and limits |
| --- | --- | --- |
| [llama.cpp issue 28211](https://github.com/ggml-org/llama.cpp/issues/28211) | A Strix Halo owner reports incorrect HIP logits after prompts cross microbatch boundaries. Qwen and Gemma examples include CPU and Vulkan controls. Host-buffer handling is implicated. | Closest hardware match; the issue was labelled unconfirmed. The tested AMD build contains a related change. Its isolated causal effect remains unproved. |
| [Ollama issue 17498](https://github.com/ollama/ollama/issues/17498) | Gemma 4 12B becomes corrupted near 1,200 prompt tokens on Radeon 8060S. Vulkan works, as does Qwen 2.5 14B under ROCm. | Same GPU family, different OS, runtime, and model. Does not identify our cause. |
| [Flash Next model discussion](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF/discussions/52) | An operator reports corrupted Flash Next output and recovery through architecture corrections. | Explicitly concerns qwen4exp. It does not establish a fix for Qwen3-8B or Gemma. |
| [Buffer-overlap fix](https://github.com/ggml-org/llama.cpp/pull/21566) | A merged change prevents unsafe fusion when source and destination buffers overlap. Gemma 4 F16 motivated the report. | Merged in April 2026. Check whether a runtime already includes it. Applicability to our quantized HIP case remains unproved. |

The host-buffer report separates GPU classification from accepting host buffers for GPU operations. Its author warns that reversing classification alone can revive another bug. A narrow, reviewed change is preferable to blindly copying a workaround. [Reported regression and proposed repair](https://github.com/ggml-org/llama.cpp/issues/28211)

### Validation design

Preserve the broken configuration and outputs. Change one factor at a time:

1. Keep model checksum, source text, template, and sampling settings identical.
2. Confirm actual GPU execution and record loaded runtime dependencies.
3. Test source-based questions with short and multi-batch inputs.
4. Repeat a bounded long-source case and inspect its answers.
5. Compare the bundled runtime with a separate upstream HIP runtime.
6. Test the suspected memory path before and after the candidate repair.
7. Preserve unsuccessful attempts and identify every configuration explicitly.

Readable output is necessary but insufficient. Correct source-based answers should survive repeated runs. Where practical, compare logits or perplexity against a working backend. Small floating-point differences are expected; substantial corruption requires investigation.

Increasing the microbatch size can isolate a boundary-sensitive bug. Passing one prompt that now fits a single batch does not establish repair. Longer inputs must also work across multiple batches.

## Performance evidence

| Source | Useful evidence | Interpretation |
| --- | --- | --- |
| [AMD Qwen3.8-27B article](https://www.amd.com/en/blogs/2026/run-qwen-3-8-27b-on-amd-ryzen-ai-max-and-radeon-graphics-cards-day-0.html) | AMD reports up to 24.5 tokens per second for this dense model on Ryzen AI Max+ 395. Its configuration uses Windows, Vulkan, and speculative decoding. | Model-specific settings warrant testing where supported. A larger parameter count does not imply 40-plus prose generation. |
| [AMD large-model article](https://www.amd.com/en/blogs/2026/amd-ryzen-ai-max-ai-pcs-deliver-exceptional-intelligence.html) | AMD also publishes LM Studio results using Ubuntu and Vulkan. | Linux is viable. Separate demonstrations do not establish an OS winner. |
| [Community HIP versus Vulkan report](https://github.com/ggml-org/llama.cpp/issues/24438) | A Strix Halo owner reports Vulkan outperforming HIP for a particular Qwen configuration. | Backend names alone do not predict performance. Versions and workloads matter. |
| [Qwen tuning repository](https://github.com/KyaniteLabs/qwen38-27b-strix-halo) | The authors distinguish high counting-test throughput from lower ordinary prose throughput. | Use representative source-based prose when judging research performance. |
| [Strix Halo hardware testing](https://github.com/lhl/strix-halo-testing/blob/main/llm-bench/README.md) | First-person experiments discuss memory bandwidth and configuration effects. | Useful leads, not measured gains on this Evo. |

A controlled matrix keeps the model, quantization, context, batch sizes, and GPU placement fixed. Record flash attention, KV-cache precision, speculative decoding, and thread count. Measure prompt processing separately from generation. Identify cold and warm cache conditions explicitly.

The completed Qwen3-8B comparison matches the laptop’s pinned b10852 source and official weights. Five repetitions follow default warmup. [Synthetic results](results/2026-09-08/evo/qwen8-synthetic-speed.md) remain distinct from application throughput. Synthetic benchmarks can complete while a serving configuration remains incorrect.

Begin tuning with a correct runtime and full GPU placement. Then test relevant memory settings, batching, and supported speculative decoding. Compare power profiles under similar thermal conditions. Driver, kernel, BIOS, and OS changes require a specific hypothesis and rollback plan.

## Digital and computational humanities

No verified scholarly review of this exact Evo X3 emerged from this search. Relevant resources instead address local deployment, evidence handling, and evaluation.

| Resource | Contribution | Evidence boundary |
| --- | --- | --- |
| [AI for Humanists workshops](https://aiforhumanists.com/workshops/) | David Mimno and Melanie Walsh list a workshop on local LLMs and long contexts. | Teaching resource, not a benchmark of this computer. |
| [Princeton CDH interview with John Ladd](https://cdh.princeton.edu/blog/2025/12/08/john-ladd/) | Discusses local models, research workloads, privacy, and sustainability. | Research context, without a controlled Evo performance comparison. |
| [Christopher Pollin's digital-humanities workshop](https://chpollin.github.io/llmdh/) | Covers prompting, context design, and structured humanities workflows. | Some exercises use hosted systems. Workflow ideas do not establish equivalent local performance. |
| [RUCAI study](https://www.cambridge.org/core/journals/computational-humanities-research/article/rucai-an-opensource-localfirst-ai-teaching-assistant-for-course-planning-and-classroom-support/3118916815A5842B4573BA25059B03A0) | Describes a local teaching assistant using document retrieval and source references. | Qualitative pilot, not controlled speed or accuracy evidence. |
| [Finnish named-entity linking study](https://seco.cs.aalto.fi/publications/2025/leal-et-al-linker-2025.pdf) | Explores local LLMs and knowledge graphs for metadata enrichment. | Preliminary, task-specific evidence cannot establish whole-book summarization reliability. |

## Applying these sources to historical evaluation

Evaluate factual correctness, citation support, and summary coverage separately. Compression can omit details without contradicting them. A citation can identify the correct page while misrepresenting it. Synthesis can introduce errors absent from individual chunk summaries.

The approved follow-up experiment uses fixed source questions and reference answers. Development and held-out passages remain separate. Freeze prompts before inspecting held-out results. Include questions whose answers are absent, allowing justified abstention.

Assess direct answers, direct summaries, and merged summaries separately. Record new synthesis errors and inherited errors. Distinguish contradictions from ambiguous phrasing and missing coverage. Count unique errors separately from repeated appearances.

This evaluates a particular model, prompt, runtime, and workflow. A failed strict benchmark does not establish general unsuitability for research. Fluent prose and high token rates likewise do not establish source fidelity.

## Publication and reproducibility

These notes accompany the [measured speed evidence](results/2026-09-08/evo/README.md), [corrected original history audit](results/2026-09-08/history/README.md), and [frozen accuracy pilot](experiments/history-v2/USAGE.md). Source provenance, prompts, retries, and failed runs are retained. Credentials, private host identifiers, and unrelated personal paths are excluded.

## Subsequent validation on the Evo

AMD's isolated September 6 build subsequently produced readable output in repeated checks. Qwen3-8B and Gemma26 each completed two short and two fifty-page tests. Requested record retrieval succeeded. This resolves the observed repetition within that bounded battery, while citation and historical accuracy remain separate.

The unchanged upstream backend still failed with the newer ROCm libraries. This supports a backend-build explanation. The AMD build contains a change disabling direct host access on gfx1151. Other code differences remain, so this experiment does not isolate that commit's effect. [Source change](https://github.com/ggml-org/llama.cpp/commit/865374bbea0a65966c5d1a79c0c1f73ac8f1bfb4), [tested AMD release](https://github.com/AMD-Ecosystem/llama.cpp/releases/tag/gfx11-rocm-nightly-20260906)

The Qwen long checks processed 15,819 prompt tokens across many microbatches. Native generation was approximately 26.14 tokens per second, versus 41.8 on short inputs. Gemma's long-check native generation was approximately 40.56 tokens per second. These are diagnostic measurements, not the completed matched speed matrix. They do not measure visible-phase timing independently.

## Evaluation identity and current boundary

The source audits use Codex-assisted text comparison, including a second Codex review. They are not independent human adjudication or PDF-image verification. The user examined selected earlier examples. Partial answers, ambiguous wording, citation defects, coverage omissions, and direct contradictions remain distinct. The [completed separated pilot](results/2026-09-08/history-v2/README.md) now supplies extraction, summary, coverage, and timing results. [Historical-research lessons](HISTORY-RESEARCH-LESSONS.md) distinguish tested findings from proposed prompting changes.

## Completed supported-profile check

The [bounded Qwen8/Gemma26 profile comparison](results/2026-09-08/power-profiles/README.md) found no meaningful overall gain from performance mode. It retained pinned Vulkan binaries and identical weights. The test restored balanced mode and both serving routes. The user subsequently selected performance for daily operation. Its built-in saved state and enabled daemon were verified without rebooting. Fixed order and limited repetitions prevent a universal performance claim.
