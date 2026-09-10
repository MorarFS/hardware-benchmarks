# MLX measurements on M4 Max

MLX 0.32.2 / mlx-lm 0.31.3 executed Qwen3-8B 4-bit inference successfully on September 10, 2026. Model and publisher SHA-256 checks passed; [exact file receipt](mlx-model-files.json) and [raw results](mlx-results.json) preserve provenance and every observation.

## Short-prompt application

One warmup, then three retained runs of the same 50-token chat prompt, greedy sampling, thinking disabled, no draft model, maximum 256 new tokens. Each stopped naturally after 187 generated tokens. Other model downloads continued throughout by explicit user instruction.

| Observation | Measured value |
|---|---:|
| Generation speed, mean ± sample SD | 89.5169 ± 0.0575 tokens/s |
| Individual generation speeds | 89.5833, 89.4851, 89.4823 tokens/s |
| Full generation-call wall time | 2.2577–2.2636 seconds |
| First nonempty content | 0.1588–0.1641 seconds |
| MLX-reported peak memory | 4.8068 GB |
| Prompt processing | 487.95–491.57 tokens/s |

This is an MLX application observation, not the llama-bench pp512/tg256 protocol or a hardware-isolated comparison. The MLX affine four-bit weights differ from the Q4_K_M GGUF artifact; APIs, prompts and timing boundaries also differ. The three runs share one session and repeated prompt. No inference result demonstrates absence of background-load effects.

MLX `load()` returned after 0.382 seconds, but lazy loading and filesystem cache make that **not a cold model-load measurement**. The warmup took 3.080 seconds, including 0.987 seconds to first content, versus ~2.26 seconds after warmup. Peak MLX allocator memory is not whole-system memory or a dedicated-VRAM counter.

The response is readable and discusses weights and KV cache. It overgeneralizes shared-memory conflicts and frequent swapping: fitting weights/cache do not themselves imply swapping. This is a smoke observation, not a factual-quality score. Full text is retained in the JSON.

## FP16 matrix observations

Synchronized MLX square matrix multiplication, fixed inputs, one warmup followed by five samples. Input allocation/random generation excluded. Mean of per-sample `2*N^3 / seconds`:

| Matrix side | Mean TFLOP/s |
|---|---:|
| 2,048 | 7.188 |
| 4,096 | 13.476 |
| 8,192 | 14.067 |

The smallest case varied substantially (5.56 to 1.65 ms), so it is not a stable peak estimate. All samples remain in the raw JSON. These kernel observations do not measure training performance, model inference throughput, or theoretical GPU peak.

## Reproduce

```sh
python3 -m venv work/mlx-env
work/mlx-env/bin/python -m pip install mlx==0.32.2 mlx-lm==0.31.3
# Download the pinned artifact into work/mlx-qwen8 using huggingface_hub.snapshot_download:
# repo_id='mlx-community/Qwen3-8B-4bit'
# revision='545dc4251c05440727734bcd94334791f6ab0192'
# Verify model.safetensors SHA-256 against mlx-model-files.json.
caffeinate -i work/mlx-env/bin/python scripts/check-m4-mlx.py
```
