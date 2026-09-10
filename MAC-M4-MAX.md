# Apple M4 Max local AI campaign

**Status: measurements and source reviews complete, September 10, 2026 (Asia/Singapore).** Seven GGUF speed suites, Qwen8 CPU/MLX controls, the 235B native-thinking capacity experiment, and the Qwen3.8-Flash-Next MLX extension are complete. All selected model files were downloaded and verified. This is a different computer from the existing M5 Pro report; historical results remain unchanged.

## Research usefulness so far

| Configuration | Visible tokens/s | Tokens/request wall second | Extraction correct / partial / other (20) | Full-source coverage complete / partial / omitted (16) |
|---|---:|---:|---|---|
| [Qwen8 Q4_K_M, Metal](results/2026-09-10/m4-max/history/qwen3-8b/README.md) |38.75|21.61|18 / 1 / 1 contradiction|3 / 9 / 4|
| [Qwen8 Q4_K_M, Metal delayed repeat](results/2026-09-10/m4-max/history-repeat/qwen3-8b/README.md) |60.81|32.89|18 / 1 / 1 contradiction|3 / 9 / 4|
| [Qwen8 group64 four-bit, MLX](results/2026-09-10/m4-max/mlx-history/README.md) |73.11|32.04|16 / 1 / 1 contradiction + 2 false abstentions|1 / 10 / 5|
| [Qwen35 UD-Q4_K_M, Metal](results/2026-09-10/m4-max/history/qwen36-35b/README.md) |75.24|46.81|18 / 2 / 0|4 / 9 / 3|
| [Gemma26 Q4_K_M, Metal](results/2026-09-10/m4-max/history/gemma4-26b/README.md) |85.46|48.92|18 / 2 / 0|6 / 7 / 3|
| [Qwen27 UD-Q4_K_M, Metal](results/2026-09-10/m4-max/history/qwen38-27b/README.md) |14.89|9.02|19 / 1 / 0|4 / 1 / 11|
| [Nemotron49 Q4_K_M, Metal](results/2026-09-10/m4-max/history/nemotron-49b/README.md) |9.27|5.19|17 / 2 / 1 contradiction|2 / 9 / 5|
| [Qwen122 UD-IQ2_XXS, Metal](results/2026-09-10/m4-max/history/qwen35-122b-iq2xxs/README.md) |33.62|17.59|17 / 2 / 1 unsupported|4 / 2 / 10|
| [Qwen3.8 Flash-Next mixed Q2/Q4, MLX](results/2026-09-10/m4-max/flash-next/history/README.md) |32.01|16.63|18 / 2 / 0|2 / 0 / 14|

The 20 extraction questions include four source-absent questions; they are not an additional denominator. Partial answers are separate from fully correct answers.

Gemma and Qwen35 exceed 40 on both observed rates. They still produce source errors and omit material; neither is an unchecked research recommendation. Qwen35’s merged output copies all four direct summaries, including their errors. Qwen27 has one more correct extraction answer, but its full-source control omits 11 compound units and its measured research rate is far below 40. MLX Qwen8 has a higher visible rate than both observed GGUF batteries, but drops an entire excerpt from synthesis; its wall rate is similar to the delayed GGUF repeat. All eight matched configurations correctly abstain on the four genuinely source-absent questions; MLX also falsely abstains on two stated answers. Nemotron completes the full 32K battery without sampled swap, but is slower than the smaller candidates and compresses three excerpts into one paragraph in its full-source answer. Qwen122 clears 40 in the short synthetic test but falls to 33.62 visible on source requests and omits all of H3 in its full-source answer. Coverage records representation separately from correctness; a represented event can still have a false outcome.

These are observations on a small selected OCR workload, with one battery per configuration and one separately reported Qwen8 GGUF repeat. Request wall rates include prompt processing but exclude startup and inter-request work. Model outputs and quantization differ; this is not an isolated backend or hardware comparison. Codex-assisted ledgers preserve all 20 extraction judgments, 48 applicable coverage judgments and grouped claims for each completed configuration (the Qwen8 repeat inherits its identical-output judgments), with no independent human adjudication.

The [delayed Qwen8 repeat](results/2026-09-10/m4-max/history-repeat/qwen3-8b/README.md) produced byte-identical answers in all 12 requests but materially different timing: 60.81 visible / 32.89 wall tokens/s versus 38.75 / 21.61 originally. This makes a stable pass/fail claim at 40 visible tokens/s premature; neither battery reaches 40 including prompt processing. A separate [context/logging diagnostic](results/2026-09-10/m4-max/context-diagnostic/README.md) decoded the same H1 request near 75 tokens/s at both 8K and 32K. The cause of run-to-run variation remains unresolved; sequential trials, different run history and unmeasured temperatures/frequencies prevent a causal interpretation. Original measurements remain unchanged.

[Same-artifact system comparison](results/2026-09-10/m4-max/matched-system-comparison.md), [synthetic speed and five-sample variation](results/2026-09-10/m4-max/speed.md), [CPU baseline](results/2026-09-10/m4-max/cpu.md), and [MLX short inference/matrix observations](results/2026-09-10/m4-max/mlx.md) remain separate from source fidelity.

![Research speed and source fidelity](results/2026-09-10/m4-max/research-comparison.png)

## Verified machine and runtime

- Apple M4 Max MacBook Pro: 16 CPU cores (12 performance, four efficiency), 40 GPU cores, 64 GiB unified memory (68,719,476,736 bytes).
- macOS 26.6, build 25G72; AC connected, Automatic power mode. Initial system swap was zero. No initial thermal/performance warning was reported by `pmset`.
- Official llama.cpp b10852 macOS arm64 release, commit `050dde50c`; archive SHA-256 `0a1bd66656354e43bc90fb7d7ce5a56c5683f338706e5d59fd4e38e7f44c4008`. Metal device `MTL0` initialized successfully. Driver recommended working set: 55,662,788,608 bytes (~51.84 GiB), not a guaranteed model capacity.
- MLX 0.32.2 and mlx-lm 0.31.3 installed in a local virtual environment. MLX reports the M4 Max GPU available. Actual MLX inference completed; three warmed short-prompt runs averaged 89.52 tokens/s. This uses different weights/quantization and timing from the GGUF protocol.
- Apple Command Line Tools installed successfully: package `26.6.0.0.1781586589`; Apple clang 21.0.0 executes. These tools support source builds; the official prebuilt llama.cpp already ran without them.

[Configuration](results/2026-09-10/m4-max/configuration.json), [MLX setup](results/2026-09-10/m4-max/mlx-configuration.json), and [capacity provenance](results/2026-09-10/m4-max/candidate-research.json) preserve the details without hardware serial numbers or UUIDs.

## Planned measurements and interpretation

The exact five original comparison artifacts are Qwen3 8B, Qwen3.6 35B-A3B, Gemma4 26B-A4B, Qwen3.8 27B and Nemotron49B, pinned in `scripts/models.json`. The prior Qwen3.5 122B UD-IQ2_XXS artifact is also included. Synthetic protocol remains five measured repetitions after default warmup; pp512 and tg256 at depth zero, then tg256 at depth 2,048; FP16 K/V, flash attention, batch/microbatch 512, ten threads, single Metal device and all layers requested. Actual placement and failures must be checked.

**The user explicitly requests downloads continue during inference.** Transfers were never paused and finished naturally during Nemotron’s source battery. Qwen122 and Qwen235 inference therefore has no pending model-download traffic; earlier tests and part of Nemotron’s battery overlap transfers. The new `scripts/run-m4-benchmark.py` preserves the original protocol but omits its download-suspension wrapper. Results therefore describe a desktop with concurrent transfers, not a controlled download-isolated experiment. Transfers can use CPU, memory buffers and SSD bandwidth even with unified memory. Their effect is unmeasured, not assumed large or zero. Retain five samples and variation; qualify load/wall timing especially. No timed inference overlapped Apple installation. Workspace analysis, plotting setup and file verification also overlapped portions of the campaign. [Aggregate background samples](results/2026-09-10/m4-max/background-downloads.json) document continuing model-file growth without publishing process paths or network addresses.

A separate CPU baseline and MLX application/kernel observations completed. MLX uses `mlx-community/Qwen3-8B-4bit` revision `545dc4251c05440727734bcd94334791f6ab0192`, which differs in weight format and quantization from the GGUF baseline. These rows must not be presented as an isolated backend comparison.

The frozen history-v2 fixtures passed all 17 integrity checks. Application tests use the existing Mac adaptation, 32K context and a declared 1,024 MiB RAM prompt-cache limit. Preserve the predeclared rubric in `experiments/history-v2-mac/README.md`; separate correctness, partial answers, citation fidelity, coverage, and instruction compliance. Judgments are Codex-assisted, not independently human-adjudicated.

## Capacity candidate

The [4K native-thinking check](results/2026-09-10/m4-max/capacity/qwen235-thinking-iq1s-ctx4096/README.md) completed: 42 and Paris were correct, with a coherent computational-cost explanation, all layers on GPU, 45.53 GiB peak sampled RSS and zero sampled swap growth. Its synthetic generation rates were 27.06 tokens/s at depth zero and 24.12 at depth 2,048. These establish actual execution of the selected artifact, not general research usefulness. The separate 16K source battery completed 11 submitted requests; synthesis was blocked by a capped parent summary. All layers remained on GPU, peak sampled RSS was 49.58 GiB, and sampled swap remained zero. The 512-token thinking budget activated on all 11 requests (7 forced ends, 4 natural ends).

Qwen3-235B-A22B-Thinking-2507 IQ1_S is selected for a bounded capacity experiment: 235B total / 22B active parameters, 47,948,249,568 bytes (~44.66 GiB) of weights. Exact publisher revision and SHA-256 are in `scripts/mac-extra-models.json`. Initial readable-output check uses 4,096 context tokens and native thinking mode, distinct from reasoning-off comparisons. A separate full-source attempt uses 16,384 context tokens, a 1,024 MiB RAM prompt cache, a 512-token budget per thinking block, and a 2,048-token overall output cap. The pinned [budget implementation](https://github.com/ggml-org/llama.cpp/blob/050dde50c/common/reasoning-budget.cpp) can rearm for a new block and finish a UTF-8 sequence before forcing its end. Actual budget activation and output receipts are retained and validated; command flags alone are insufficient.

IQ1_S is aggressive quantization and can damage quality. A file below physical memory does not prove usability. Retain actual layer placement, memory pressure, system swap growth, process RSS, failures, readable output, and context. A one-GiB swap-growth guard stops excessive paging; it does not prove zero paging. No GPU memory limits are raised. Larger inspected recipes are documented as preflight exclusions. This is a selected candidate search, not a universal largest-model claim.

## Reproduction

```sh
sh scripts/setup-mac.sh
python3 scripts/get-model.py qwen3-8b
caffeinate -i python3 scripts/run-m4-benchmark.py qwen3-8b --output local-results/m4-max-speed --timeout-seconds 1200
python3 scripts/history_v2/runner.py validate
caffeinate -i python3 scripts/history_v2/run_mac.py qwen3-8b --output local-results/m4-max-history/qwen3-8b --cache-ram-mib 1024
# After downloading the separately pinned capacity artifact:
python3 scripts/get-model.py qwen235-thinking-iq1s
caffeinate -i python3 scripts/check-m4-capacity.py qwen235-thinking-iq1s --context 4096
caffeinate -i python3 scripts/history_v2/run_m4_capacity.py qwen235-thinking-iq1s --context 16384 --cache-ram-mib 1024 --output local-results/m4-capacity-history
python3 scripts/history_v2/collect_m4_capacity.py qwen235-thinking-iq1s --source local-results/m4-capacity-history --output results/2026-09-10/m4-max/capacity-history/qwen235-thinking-iq1s
python3 scripts/history_v2/retokenize_m4.py qwen235-thinking-iq1s --evidence-root results/2026-09-10/m4-max/capacity-history
```

Run only one inference workload at a time on AC. Model downloads may continue by the stated user policy. Each model download verifies SHA-256 before promotion. Source builds, downloads, unreviewed raw logs and model weights remain local. Measured results and sanitized reproducible evidence will be added incrementally to `results/2026-09-10/m4-max/`.

## Native-thinking 235B source results

[Complete evidence and review](results/2026-09-10/m4-max/capacity-history/qwen235-thinking-iq1s/README.md). Among identifiable visible answer statements, 19 of 20 were source-correct and one confused who removed Romanus. This is not a clean-answer success rate: only H2 supplied a clean complete extraction block; H1 supplied final answers after planning leakage, H3 mixed answer statements into planning and ended with only two final answers, and H4 never delivered its promised final block. H1’s summary exhausted 2,048 output tokens in repetitive planning, so the dependent merged summary was not submitted.

The final full-source summary covered 4 of 16 units completely, 8 partially, and omitted 4. It conflated the literary emperors with Ottoman-era decline and added unsupported attributions and mechanisms. Across the ledger, 28 coverage units are assessed and 20 remain explicitly unassessed (the missing H1 final summary and unsubmitted synthesis). Source-statement accuracy, final-answer delivery, quotation quality, and coverage remain separate.

Nine held-out submitted requests produced 6,182 retokenized API-content tokens: **15.7578 content tokens/s during the visible phase**, or **6.1624 content tokens/s over request wall time**. These totals include leaked planning and repetition and must not be described as final-answer throughput. This native-thinking profile remains outside the matched reasoning-off chart.

## Qwen3.8-Flash-Next MLX: fits with disk-backed PLE, weak synthesis

The [full evidence](results/2026-09-10/m4-max/flash-next/README.md) records the faithful Sawfwair mixed Q2/Q4 artifact at `a6e3d7a43efb8803cd6b847299a54084dc4e8ef4`, converted from official Qwen at `f5d08274bafd880402bd16f5e3e6c514136ec06c`. Its complete download is 68.10 GiB, including 29.80 GiB of n-gram tables and the 1.39 GiB optional MTP head. All 48 layers and all 512 experts per bank are retained. Target-only decoding loads 36.89 GiB of target/vision weights while the full PLE table is mapped read-only and requested rows are copied to MLX. MTP is not enabled.

The first strict load succeeded but generated garbage. The publisher’s converter stores shifted text normalization scales as `raw_weight + 1`; upstream MLX-VLM added 1 again. The scoped [runtime compatibility helper](scripts/flash_next_compat.py) uses the stored scales directly, preserving every checkpoint tensor and leaving gated/vision norms unchanged. The failed run is retained separately. All subsequent results use this explicit correction with MLX 0.32.2 and MLX-VLM 0.7.0 at `8f5dc3ddddbb8d7dd2b88ac51015def6f81fed21`, in an isolated environment.

Three warm short runs generated 199 tokens each at **36.4883 ± 0.1067 tokens/s**, with identical output text and mean request wall time 5.733 seconds. Peak MLX allocation was **40.7525 GB** (37.95 GiB). The preliminary arithmetic/capital answers were correct and the prose readable, but the explanation did not follow the requested three-sentence format and the separate hardware prose contained overgeneralizations. This is a coherence/fit check, not an accuracy benchmark.

All 12 frozen source requests finished naturally; ten held-out requests yielded 5,255 visible tokens over 164.1763 visible-phase seconds and 315.9054 request-wall seconds: **32.0083 visible tokens/s**, **16.6347 tokens/wall second**. Extraction was **18 correct, 2 partial**, including all four correct source-absent responses. The partial answers omit Romanus’s forced abdication and the Mustaphas’ uncle/brother relationships. H1–H3 omit the required supporting quotations.

The merged summary copies the four direct summaries exactly after whitespace normalization: 1,025 words instead of the requested 350–450. The full-source control receives 13,916 tokenized input tokens but returns 784 words solely about H1’s opening narrative. It stops normally at 1,036 generated tokens, below the 2,048 cap. It completely covers only 2 of 16 units and omits 14, including all of H2–H4 and H1’s later battles/defensive ending. Source errors elsewhere include misidentifying Constantine as Leo’s grandson and losing several qualifications.

Separate post-result context checks retrieve all three queried names from the 13,805-token source and all three synthetic markers at 3,839 and 15,317 input tokens. They demonstrate access to later input and do not support a simple truncation explanation for the failed synthesis; they neither replace its score nor rule out subtler runtime issues. The model’s advertised 262,144-token maximum was not tested.

The source battery peaks at **41.7855 GB MLX allocation** and **28,152,463,360 bytes sampled RSS**; these counters overlap and must not be added. Source testing shows no swap growth above an existing approximately 123 KiB. The subsequent context diagnostic peaks at 41.8318 GB MLX allocation and increases **system-wide swap by approximately 390 MiB**. Its cause cannot be isolated from these desktop measurements. This configuration executed on 64 GB with full disk-backed PLE, but the overall experiment was not swap-free.

Reproduction requires Python 3.12 and the retained environment pins. The converter reference, download hashes, tensor inventory, storage/architecture checks, failed initial run, fixed run, source ledger, and context diagnostics are under the evidence directory.

```bash
python3.12 -m venv work/flash-next-env
work/flash-next-env/bin/pip install -r results/2026-09-10/m4-max/flash-next/runtime-packages.txt
work/flash-next-env/bin/python scripts/get-m4-flash-next.py --output work/mlx-flash-next-source --receipt local-results/flash-next-download.json
python3 scripts/prepare-m4-flash-next.py --source work/mlx-flash-next-source --output work/mlx-flash-next-external-ple
caffeinate -i work/flash-next-env/bin/python scripts/check-m4-flash-next.py --model work/mlx-flash-next-external-ple --output local-results/flash-next-smoke
caffeinate -i work/flash-next-env/bin/python scripts/history_v2/run_m4_flash_next.py --model work/mlx-flash-next-external-ple --output local-results/flash-next-history
caffeinate -i work/flash-next-env/bin/python scripts/check-m4-flash-context.py --model work/mlx-flash-next-external-ple --output local-results/flash-next-context
work/flash-next-env/bin/python scripts/validate-m4-flash-next.py --model work/mlx-flash-next-source
```
