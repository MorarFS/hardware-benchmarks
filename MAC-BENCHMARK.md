# Reproduce the speed baseline on Apple Silicon

Start with the official Qwen3-8B Q4_K_M baseline. It matches the Windows and Evo comparisons. This guide prepares a Mac/Metal comparison; no Mac model download, build, or inference was performed during publication.

The target Mac has 48 GB unified memory. That is shared by macOS, applications, weights, KV cache, and working buffers. It is not a 48 GB model-file allowance. The Evo's exact GPT-OSS120 file alone is 63.39 GB, so it cannot fit entirely within that physical capacity. Flash Next and DeepSeek shards also require separate capacity checks. Begin with Qwen8, then test compatible smaller installed files individually. Changing quantization creates a new configuration, not a matched result.

## Exact baseline

- Repository: `Qwen/Qwen3-8B-GGUF`.
- Revision: `7c41481f57cb95916b40956ab2f0b139b296d974`.
- File: `Qwen3-8B-Q4_K_M.gguf`, 5,027,783,488 bytes.
- SHA-256: `d98cdcbd03e17ce47681435b5150e34c1417f50b5c0019dd560e4882c5745785`.
- llama.cpp: tag `b10852`, source commit prefix `050dde50c`.

The [pinned official model](https://huggingface.co/Qwen/Qwen3-8B-GGUF/tree/7c41481f57cb95916b40956ab2f0b139b296d974) defines the weight baseline. The existing Windows scripts use the same hash.

## Build the pinned Metal runtime

Use an Apple Silicon Mac with Xcode Command Line Tools, CMake, Git, and Python 3.10+. Install missing prerequisites through your usual setup. The following commands run only when you execute them:

```sh
git clone https://github.com/MorarFS/hardware-benchmarks.git
cd hardware-benchmarks
mkdir -p work
git clone --branch b10852 --depth 1 https://github.com/ggml-org/llama.cpp.git work/llama.cpp
git -C work/llama.cpp rev-parse HEAD
cmake -S work/llama.cpp -B work/llama.cpp/build -DCMAKE_BUILD_TYPE=Release -DGGML_METAL=ON
cmake --build work/llama.cpp/build --config Release -j 8 --target llama-bench llama-server
work/llama.cpp/build/bin/llama-server --version
work/llama.cpp/build/bin/llama-bench --list-devices
```

Confirm the commit begins `050dde50c`. Metal is enabled by default on macOS; the explicit option documents intent. Keep the build's adjacent runtime resources intact. See the [pinned build guide](https://github.com/ggml-org/llama.cpp/blob/050dde50c/docs/build.md#metal-build).

Select the exact Metal device identifier printed by `--list-devices`. Replace `METAL_DEVICE_FROM_LIST` below with that identifier. Do not assume device names match another machine.

## Download or reuse the exact Qwen8 file

Skip downloading if you already have the verified file. Otherwise:

```sh
curl --fail --location --output work/Qwen3-8B-Q4_K_M.gguf 'https://huggingface.co/Qwen/Qwen3-8B-GGUF/resolve/7c41481f57cb95916b40956ab2f0b139b296d974/Qwen3-8B-Q4_K_M.gguf?download=true'
shasum -a 256 work/Qwen3-8B-Q4_K_M.gguf
```

Check the hash above before running. The Python runner verifies it again.

## Run the matched protocol

Close competing GPU workloads. Record the chip, macOS version, unified memory, power mode, AC state, and relevant background activity. Use a new output folder for each run.

```sh
python3 scripts/Run-Benchmark.py --executable work/llama.cpp/build/bin/llama-bench --device METAL_DEVICE_FROM_LIST --backend Metal --model work/Qwen3-8B-Q4_K_M.gguf --output work/mac-qwen8-metal
```

Add `--dry-run` to inspect both commands without loading anything. Add `--metadata path/to/machine.json` to save your reviewed machine and power settings. The runner does not change power settings or install software.

The fixed protocol is:

| Setting | Value |
| --- | --- |
| Prompt processing | `pp512`, depth 0 |
| Generation | `tg256`, initial depth 0 and 2048 |
| Repetitions | Five measured samples per test |
| Warmup | llama-bench default enabled |
| GPU / split | `-ngl 99`, `-sm none`, selected Metal device |
| Flash attention | `-fa on` |
| K/V cache | `-ctk f16 -ctv f16` |
| Batch / microbatch | `-b 512 -ub 512` |
| CPU threads | `-t 10` |
| Speculation | OFF; no MTP/draft model, sampling, or chat template |
| Deadline | 900 seconds per depth; retain failures |

These flags are supported by the pinned benchmark. The runner checks executable help, runtime version, measured backend/device, build commit, GPU-layer request, depth, and sample count. Read verbose loader logs to verify actual full layer placement and identify partial offload. Requested `-ngl 99` alone is not placement proof. See the [pinned llama-bench reference](https://github.com/ggml-org/llama.cpp/blob/050dde50c/tools/llama-bench/README.md).

For another compatible GGUF, use its exact model path and supply its expected SHA-256:

```sh
python3 scripts/Run-Benchmark.py --executable work/llama.cpp/build/bin/llama-bench --device METAL_DEVICE_FROM_LIST --backend Metal --model /path/to/compatible-model.gguf --sha256 EXPECTED_MODEL_SHA256 --output work/mac-other-model
```

For sharded GGUFs, supply the first shard. The runner requires every shard and records all hashes. `--sha256` verifies the first shard; compare the remaining recorded hashes with the Evo `model-files.json` before calling it matched. Hashing does not establish capacity or architecture support. Retain OOM, unsupported-architecture, timeout, or placement failures. Do not quietly substitute weights, reduce settings, or accept CPU fallback.

## Interpret and share results

`pp512` measures processing 512 synthetic prompt tokens. `tg256` measures generating 256 synthetic tokens after the specified prefill depth. Depth 2048 is not a 65,536-token chat context setting. Report means, sample standard deviations, and all five samples.

These tests exclude chat-template rendering, tokenization, sampling, and meaningful prose evaluation. They do not measure factual accuracy or visible-answer latency. Compare them only with the [Evo synthetic table](results/2026-09-08/evo/vulkan-model-speed.md) and the corresponding Windows synthetic runs. Keep [application prose timings](results/2026-09-08/evo/amd-speed-comparison.md) separate.

Process wall time includes loading and warmup. It is not pure model-load time. Timed pp/tg excludes loading. Filesystem cache is uncontrolled, and the runner does not flush it. A cold-load experiment needs its own stated protocol and separate results. Do not add overlapping unified-memory counters together.

The same source revision, GGUF hashes, and settings give a device-plus-backend comparison: Mac/Metal versus Evo/Vulkan or Windows/SYCL/CUDA/Vulkan. They do not isolate hardware alone. Keep different versions, quantizations, offload levels, or cache settings in separately labeled rows. Five within-run repetitions are not five independent sessions.

Share the JSON samples, protocol manifest, model hashes, and reviewed offload evidence. Inspect local logs and metadata for personal paths before publishing. The existing raw-output folders remain ignored by Git.

## What was checked

The portable runner's help and dry-run command construction were checked. An offline fake executable exercises both depths, five-sample validation, version checks, output preservation, and hash rejection. The actual b10852 Linux executable help confirmed the required flags. The underlying protocol already ran on the Evo. No Metal throughput, model fit, or Mac build success is claimed here.

## Current handoff for the running Mac task

[MAC-HANDOFF.md](MAC-HANDOFF.md) requests the existing comparisons and a bounded search for the largest practical historical-work model on the user-reported 48 GB Mac. It preserves ongoing runs and distinguishes capacity, speed, and source fidelity.
