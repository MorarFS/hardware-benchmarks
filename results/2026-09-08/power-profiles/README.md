# Supported power-profile comparison

Performance mode produced no meaningful overall speed gain in this bounded comparison. Balanced Vulkan remains the preferred tested default for these workloads. The original balanced profile and both serving services were restored successfully.

The experiment used installed Qwen3-8B Q4_K_M and Gemma26 UD-Q4_K_M files. Both profiles used the same pinned Vulkan b10852/050dde50c binaries. Exact file hashes, commands, outputs, and sensor records accompany this report.

## Synthetic measurements

| Model | Measurement | Balanced tokens/s | Performance tokens/s | Change |
| --- | --- | ---: | ---: | ---: |
| Qwen8 | pp512 | 1,276.35 | 1,201.73 | −5.85% |
| Qwen8 | tg256, depth 0 | 43.69 | 43.63 | −0.13% |
| Qwen8 | tg256, depth 2048 | 41.00 | 40.88 | −0.31% |
| Gemma26 | pp512 | 1,250.60 | 1,235.70 | −1.19% |
| Gemma26 | tg256, depth 0 | 52.21 | 51.99 | −0.42% |
| Gemma26 | tg256, depth 2048 | 47.45 | 47.45 | −0.01% |

Each row retains five repetitions and sample standard deviation. Default warmup was enabled. Full GPU offload, F16 caches, flash attention, batch 512, microbatch 512, and ten CPU threads were fixed. Synthetic generation did not invoke reasoning, sampling, chat templates, or speculative decoding.

The [synthetic CSV](synthetic-results.csv) retains all 60 samples across 12 rows. These new measurements supplement the earlier baseline; they do not replace it.

## Readable prose and latency

| Model | Profile | Visible-phase range | Two-trial mean | First-visible range | Request wall range |
| --- | --- | ---: | ---: | ---: | ---: |
| Qwen8 | Balanced | 37.87–39.09 tokens/s | 38.48 | 3.09–3.16 s | 13.43–13.73 s |
| Qwen8 | Performance | 37.91–38.14 tokens/s | 38.03 | 3.20–3.33 s | 13.79–13.88 s |
| Gemma26 | Balanced | 45.25–45.61 tokens/s | 45.43 | 4.97–5.01 s | 11.06–11.24 s |
| Gemma26 | Performance | 45.62–45.82 tokens/s | 45.72 | 4.92–4.94 s | 10.97–11.14 s |

Gemma’s highest observed two-trial mean was 0.63% higher under performance. Qwen’s mean was 1.19% lower. This small sample does not establish a dependable Gemma gain.

All eight outputs were readable and stopped normally without caps or reasoning. Paired trial numbers produced identical text across profiles. The two trials within each profile differed, so deterministic reproduction is not claimed.

Readability does not establish historical accuracy. Qwen omitted the requested citations, exceeded the word request, and sometimes lost the passage’s ending. One output introduced Gratian where the supplied account names Valentinian. These checks do not constitute another full accuracy evaluation.

The standalone server used context 8192, parallel 1, seed 42, temperature 0, and reasoning OFF. Each prompt included H1’s supplied source and requested 180–220 words. Both models reported 3,318 prompt tokens. Every request reported zero cached prompt tokens.

Visible-phase rates begin at the first visible fragment and include final-response overhead. Prompt processing, first-visible delay, total latency, and native generation rates remain separately recorded. See [prose results](prose-results.csv).

Gemma exceeded the updated preference of 40 visible tokens/s in this prose check. Qwen8 did not, although its depth 2048 synthetic rate exceeded 40. The original 35-token requirement remains a separate historical threshold.

## Power and thermal observations

The supported performance profile changed the CPU governor and EPP to performance. Balanced used powersave with balance_performance EPP. This profile change did not replace drivers or change firmware.

| Model | Profile | Peak CPU Tctl during prose | Peak GPU edge during prose |
| --- | --- | ---: | ---: |
| Qwen8 | Balanced | 70.50°C | 72°C |
| Qwen8 | Performance | 78.13°C | 78°C |
| Gemma26 | Balanced | 75.13°C | 76°C |
| Gemma26 | Performance | 76.13°C | 76°C |

One-second sysfs samples record driver-reported PPT, temperatures, clocks, governor, and EPP. The [sensor summary](sensor-summary.csv) retains each measurement interval separately. PPT is a driver sensor, not measured wall-plug consumption.

Intervals include their recorded startup, warmup, prompt, and generation portions as applicable. They are not isolated energy measurements for timed decode. CPU and GPU sensor domains can overlap on this APU. Memory figures likewise overlap across RAM, VRAM, GTT, RSS, and PSS. None were added into an artificial total.

Profiles ran in fixed order: Qwen balanced/performance, then Gemma balanced/performance. There was no randomized crossover, thermal stabilization protocol, or OS cache flush. Later performance trials were generally warmer. The experiment therefore cannot isolate profile effects from order and thermal history.

## Reproduction and restoration

Use the same verified weights and pinned binary. Record available profiles with powerprofilesctl, along with the current profile. Run only one GPU benchmark at a time. Save separate output directories for each profile and restore the original afterward.

The portable synthetic command is:

~~~sh
python scripts/Run-Benchmark.py --executable /path/to/llama-bench --device Vulkan0 --backend Vulkan --model /path/to/model.gguf --sha256 EXPECTED_SHA256 --expected-commit 050dde50c --output work/PROFILE-MODEL
~~~

The [archived deployed runner](deployed-runner.py) preserves this experiment’s exact orchestration. Its private-path placeholders and original helper dependencies make it an execution record, not a portable entry point. Exact standalone prose server commands and request payloads are included under [raw evidence](raw/).

The exclusive benchmark lock prevented overlapping measured jobs. Optional ROCm serving was paused only after an idle check. The finite service completed successfully at 13:16:23 UTC on 8 September 2026. Its terminal record contains no errors. Balanced mode, LM Studio serving, and the optional repaired ROCm service were verified restored.

This establishes the best observed configurations within a limited comparison. It does not establish the machine’s universal maximum. Further experiments were not launched.
