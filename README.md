# Local GPU inference benchmarks

Windows laptop measurements from September 8, 2026, comparing an external Intel Arc Pro B70 with an internal NVIDIA RTX 5060 Laptop GPU using the same Qwen3 model. These measure this complete machine and software configuration, including the external GPU connection.

**Preliminary snapshot:** Intel Vulkan's unusual depth-0 result needs a repeat. Intel SYCL is being tested. OpenVINO has not yet produced a verified GPU result; CPU fallback is excluded. These results do not establish Intel's best backend or either GPU's maximum throughput.

## Hardware and setup

| Component | Configuration |
| --- | --- |
| CPU | AMD Ryzen AI 9 365 |
| System memory | Approximately 16 GB |
| External GPU | Intel Arc Pro B70, 32 GB VRAM, through a detected Intel TBT5 USB4 dock |
| Internal GPU | NVIDIA GeForce RTX 5060 Laptop GPU, 8 GB VRAM |
| Drivers | Intel 32.0.101.8805; NVIDIA reported 610.88 |
| Power | AC connected |

The Intel workstation driver was installed from Intel's official package after signature and hash verification. Windows initially reported Code 43; restarting cleared it and device/display health checks passed. No driver binaries or diagnostic logs are included. The detected dock does not prove the negotiated link speed or effective PCIe bandwidth.

## Model and method

- Official **Qwen/Qwen3-8B-GGUF**, **Qwen3-8B-Q4_K_M.gguf**, approximately 5.02 GB (5,021,827,072 bytes).
- Model revision: `7c41481f57cb95916b40956ab2f0b139b296d974`.
- Verified SHA-256: `d98cdcbd03e17ce47681435b5150e34c1417f50b5c0019dd560e4882c5745785`.
- Official llama.cpp **b10852**, commit `050dde50c`; Windows Vulkan and CUDA 13.3 packages for the completed comparison.
- Sequential single-device runs, full GPU offload (`-ngl 99`), no tensor split (`-sm none`), flash attention on, FP16 K/V cache, batch/microbatch 512, ten CPU threads.
- Five measured repetitions after llama-bench's default warmup. Generate 256 tokens at initial context depths 0 and 2,048. Separately process 512 prompt tokens at depth 0.
- Values are mean tokens/second and sample standard deviation reported by llama-bench. Prefilled depth is not an application context-window setting. llama-bench excludes tokenization and sampling; this is not end-to-end chat latency.

## Measured results

| Run | Test | Initial depth | Mean tokens/s | SD tokens/s |
| --- | --- | ---: | ---: | ---: |
| intel-vulkan-depth0 | Prompt processing 512 | 0 | 2548.869875 | 223.324914 |
| intel-vulkan-depth0 | Generation 256 | 0 | 20.229451 | 0.169184 |
| intel-vulkan-depth2048 | Generation 256 | 2048 | 45.686410 | 0.089258 |
| nvidia-cuda-depth0 | Prompt processing 512 | 0 | 2499.242882 | 198.107840 |
| nvidia-cuda-depth0 | Generation 256 | 0 | 67.091562 | 0.795381 |
| nvidia-cuda-depth2048 | Generation 256 | 2048 | 62.005866 | 1.415181 |
| nvidia-vulkan-depth0 | Prompt processing 512 | 0 | 2219.146074 | 162.169020 |
| nvidia-vulkan-depth0 | Generation 256 | 0 | 64.397618 | 1.155568 |
| nvidia-vulkan-depth2048 | Generation 256 | 2048 | 60.081314 | 0.145006 |

The Intel depth-0 Vulkan figure is retained exactly as measured, pending investigation. Do not treat its difference from depth 2,048 as an established context-length effect. Vulkan provides a common-backend comparison; CUDA adds an NVIDIA-specific backend.

Machine-readable JSON in `results/2026-09-08/` retains original measured values and samples. Only the absolute model path is replaced with its basename. Original `gpu_info` lists enumerated adapters, not necessarily the selected GPU: use `devices` and the clean summary's `selected_gpu`. Intel Vulkan selected `Vulkan1`; NVIDIA Vulkan selected `Vulkan2`; NVIDIA CUDA selected `CUDA0`.

## Reproduce

Use PowerShell on Windows with compatible, healthy GPU drivers and AC power. Device IDs can differ between machines and backend packages.

1. Run `./scripts/Get-Model.ps1` to download the pinned official model and verify its SHA-256.
2. Download the Windows Vulkan and CUDA 13 packages from the [b10852 release](https://github.com/ggml-org/llama.cpp/releases/tag/b10852). Extract into separate `work/llama-vulkan` and `work/llama-cuda` directories. Add the release's CUDA 13.3 DLL package to the CUDA directory if needed. Preserve the accompanying DLLs.
3. Run each executable with `--list-devices`. Select the intended physical GPU explicitly. The script accepts configurable executable, model, device and output paths.
4. Run these commands sequentially, replacing device IDs with your enumeration:

```powershell
./scripts/Run-Benchmark.ps1 -Executable ./work/llama-vulkan/llama-bench.exe -Device Vulkan1 -RunName intel-vulkan
./scripts/Run-Benchmark.ps1 -Executable ./work/llama-vulkan/llama-bench.exe -Device Vulkan2 -RunName nvidia-vulkan
./scripts/Run-Benchmark.ps1 -Executable ./work/llama-cuda/llama-bench.exe -Device CUDA0 -RunName nvidia-cuda
```

Inspect local logs for actual GPU offload and fallback before sharing results. Raw local logs stay ignored. The reusable scripts were syntax-checked; this publishing task did not rerun GPU workloads. Measured data came from the original benchmark invocation with the same settings (FP16 KV used the runtime default).

## Limits and pending work

One laptop, one model/quantization, one session and short generation tests cannot isolate hardware performance. Power limits, temperatures, background load, link bandwidth and run order were not controlled as a laboratory experiment. Five within-run samples are not five independent sessions. No energy, quality, tokenization, sampling, application latency or concurrency benchmark was performed.

SYCL and OpenVINO 2026.3.1 runtime packages were also obtained for investigation. SYCL detects the B70; verification and additional measurements are pending. OpenVINO CPU fallback is not a GPU result. Additional completed runs will be labeled separately rather than silently replacing these observations.

## Sources

- [Pinned official Qwen GGUF files](https://huggingface.co/Qwen/Qwen3-8B-GGUF/tree/7c41481f57cb95916b40956ab2f0b139b296d974)
- [Official llama.cpp b10852 release and runtime downloads](https://github.com/ggml-org/llama.cpp/releases/tag/b10852)
- [llama-bench source and documentation at the measured commit](https://github.com/ggml-org/llama.cpp/tree/050dde50c/tools/llama-bench)
- [Intel Arc Pro Windows driver](https://www.intel.com/content/www/us/en/download/741626/intel-arc-pro-graphics-windows.html)

