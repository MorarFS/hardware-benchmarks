# Handoff to the running Mac benchmark task

The user requests this handoff for the Codex task already benchmarking their Mac. Preserve its running jobs and completed results. Do not start duplicate GPU workloads.

The user reports a MacBook Pro with M5 Pro and 48 GB unified memory. Verify the actual chip, core counts, physical memory, macOS version, and runtime. No Mac measurements are asserted in this note. Its publisher cannot verify whether the separate task has read or executed it.

## Required comparisons

The ultimate target is above 40 visible generated tokens per second with useful historical-source fidelity. Keep speed, waiting time, source support, coverage, and instruction compliance separate.

1. Continue the existing matched comparisons where compatible. Begin with the official Qwen3-8B Q4_K_M baseline. Include the evaluated Qwen35 and Gemma26 profiles where feasible.
2. Evaluate the largest practical model that fits this Mac for historical text work.
3. Run the frozen history-v2 suite separately from synthetic speed measurements.
4. Publish Mac results and reproduction steps in a dedicated results subdirectory.

Use the [Mac guide](MAC-BENCHMARK.md), [Evo speed package](results/2026-09-08/evo/README.md), [Arc model comparison](MODERN-MODELS.md), and exact model manifests as references. Do not silently substitute quantizers or weight files.

## Capacity candidate

Identify current supported candidates using primary model and runtime sources. Select a bounded capacity candidate with room for macOS, runtime overhead, and KV cache. The required long-source workload must remain usable.

The existing GPT-OSS120 MXFP4 file is approximately 63 GB. It does not fit entirely within 48 GB physical memory. A smaller quantization would constitute a separate artifact and configuration. Document its source, precision, and potential quality tradeoffs.

Record model parameters and active parameters for mixture-of-experts models. Preserve exact file bytes, SHA-256, quantization, context length, and actual offload. Record peak process and system memory, memory pressure, swap, loading time, and failures.

Loading through substantial swapping does not demonstrate usable capacity. Check sustained readable generation and the required source workload. A fitting model below the speed target remains a documented capacity result. Do not declare a universal maximum from a limited candidate search.

Keep this exploration separate from matched comparisons. Do not overwrite failed or smaller-model results.

## Speed and reasoning

The matched baseline uses llama.cpp b10852, commit 050dde50c. Use Metal on the Mac and record all actual flags.

The standard protocol uses pp512 at depth 0 and tg256 at depths 0 and 2,048. Retain five measured repetitions after default warmup, full GPU offload, F16 K/V caches, flash attention, batch/microbatch 512, and ten CPU threads. Record unsupported settings and deviations.

Synthetic generation does not invoke reasoning, sampling, chat templates, or speculative decoding. Report it separately from server decode and retokenized visible speed. Also retain first-visible delay and total request wall time.

For historical application runs, distinguish reasoning from MTP/speculative decoding. Evo Qwen35 used MTP ON with reasoning OFF. Evo Gemma used reasoning OFF. Evo GPT-OSS120 used template-default medium. Arc history runs used reasoning and MTP OFF.

## Source grading

Use the unchanged [frozen history-v2 suite](experiments/history-v2/USAGE.md). Preserve its 17 fixture hashes, prompts, source passages, and development split. Gold references must not enter model requests.

Choose and document a common rubric before examining new Mac outputs. Retain existing Mac judgments if results have already been reviewed. Do not silently regrade after seeing results.

The [Arc report](results/2026-09-08/arc-history-v2/README.md) preserves two conventions: initial strict completeness and a secondary Evo-content crosswalk. The [Evo report](results/2026-09-08/history-v2/README.md) separates 16 answerable questions from four absent-answer questions. These conventions must not be mixed into apparent hardware effects.

Record supported answers, partial answers, false abstention, and contradictions separately. Correct absence answers require checking the complete supplied passage. Citation support, quotation fidelity, summary coverage, causal relationships, and word limits need separate review.

Distinguish inherited synthesis errors from new errors. Full-source controls receive original passages, so repeated errors there are independent recurrence. Nineteen supported responses out of 20 do not establish perfect reliability or general historical accuracy.

Use source-linked evidence and identify Codex-assisted judgments. Do not describe them as independent human adjudication.

## Publication

Use a distinct directory, for example results/DATE/mac-history-v2 and a separate Mac speed directory. Publish exact configurations, methodology, model/source provenance, safe sanitized logs, raw outputs, failures, and reproduction instructions.

Fetch before integration and preserve concurrent Evo, Arc, and laptop work. Avoid force pushes. Exclude credentials, private host identifiers, personal paths, and unrelated files.

The user's current Evo daily setting is performance mode. Earlier Evo baseline measurements remain labeled balanced. That later preference does not change historical benchmark conditions.

This file conveys the user's request to the Mac’s existing executor. The Evo task has published the note only. It has neither started Mac tests nor verified their execution.
