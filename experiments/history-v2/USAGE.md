# Run the frozen accuracy pilot elsewhere

This package reproduces the separated source-fidelity prompts and request sequence. It contains no completed accuracy scores. Generation on the Evo and source adjudication remain separate work.

The original 17 fixture hashes and `freeze.json` remain unchanged. This guide and `METHOD-NOTES.md` sit outside that frozen manifest. Do not edit frozen files to adapt a run. Preserve the original suite, create a versioned copy, and document any methodological change.

## Requirements

- Python 3.10 or newer. The portable runner uses only the standard library.
- LM Studio with its **native `/api/v1/chat` streaming API** and `/api/v1/models` endpoint enabled.
- Installed model weights and sufficient memory for the selected profile at 65,536 context tokens.
- A model loaded with parallel capacity 1, flash attention, full GPU offload, and F16 KV cache. Keep its configured MTP setting below.

The native protocol was exercised with LM Studio's llama.cpp Vulkan 2.33.0 runtime. This is not a generic OpenAI-compatible `/v1/chat/completions` client. Other server versions may reject fields or emit different events. HTTP errors and raw SSE events are retained.

## Get and validate the package

```sh
git clone https://github.com/MorarFS/hardware-benchmarks.git
cd hardware-benchmarks
python scripts/history_v2/runner.py --help
python scripts/history_v2/runner.py validate
python -m unittest discover -s scripts/history_v2 -p test_runner.py -v
```

Use `python3` instead of `python` where needed. The same runner commands work in PowerShell. Tests use a local mock HTTP server; they do not download models or establish accuracy.

## Choose a frozen profile

| Profile | Installed weight file | Reasoning | MTP |
| --- | --- | --- | --- |
| `gemma26-off` | `gemma-4-26B-A4B-it-UD-Q4_K_M.gguf` | OFF | OFF |
| `qwen35-off-mtp` | `Qwen3.6-35B-A3B-UD-Q4_K_M.gguf` | OFF | ON, maximum draft 3 |
| `gptoss120-medium` | `gpt-oss-120b-MXFP4.gguf` | Template default medium | OFF |

Exact publishers, weight hashes, and sampling settings are in `configurations.json`. Model downloads are never automatic. Use `lms ls --json` to identify the installed model key. For example, replacing `YOUR_INSTALLED_MODEL_KEY`:

```sh
lms load YOUR_INSTALLED_MODEL_KEY --identifier history-gemma --gpu max --context-length 65536 --parallel 1 --no-speculative-draft-mtp --ttl 7200 -y
```

Enable flash attention and F16 K/V cache in the model's load settings before loading. For Qwen35, replace `--no-speculative-draft-mtp` with `--speculative-draft-mtp --speculative-draft-max-tokens 3`. Do not point the runner at an MTP-only sidecar. For GPT, inspect the actual chat template and confirm `Reasoning: medium` before treating it as the frozen medium profile.

The CLI exposes no seed flag. The frozen seed-42 intention cannot be guaranteed by that loading command. Record the actual seed, backend, cache type, and GPU placement from your server settings/logs. Do not call an unverified seed fixed. See the method notes for the Evo deviation.

## Inspect payloads without inference

```sh
python scripts/history_v2/runner.py plan --profile gemma26-off --model-id history-gemma --output work/history-v2-plan
```

This writes 11 source-based payloads. The twelfth uses four generated summaries and can only be assembled later. Request construction reads prompts, questions, and passage text. It cannot access parsed gold answers or coverage ledgers. Gold files are hashed as bytes for freeze integrity only.

## Run one loaded model

```sh
python scripts/history_v2/runner.py run --profile gemma26-off --model-id history-gemma --output work/history-v2-gemma
```

For a different API address, add `--base-url http://127.0.0.1:1234`. Supply the server root, without `/v1`. Authentication uses the environment variable named by `--api-key-env`, defaulting to `LM_STUDIO_API_KEY`. The secret value is never written into request files or command metadata. Set it through your normal local secret-management workflow.

Add `--model-file path/to/model.gguf` to verify the exact frozen weight hash. Without it, weights are explicitly recorded as unverified. Add `--loaded-settings path/to/settings.json` to attach operator-reviewed backend, full-offload, F16, seed, and template metadata. Native model-list checks verify context, concurrency, MTP, flash attention, and GPU KV offload. They cannot independently prove every backend detail.

Run the other two profiles sequentially after loading their matching models. The direct runner neither loads nor unloads models. It does not alter global runtime preferences or serving configuration.

## Request order and records

Each model receives 12 independent requests:

1. Development extraction and development summary, using PDF pages 101–106.
2. Extraction and direct summary for each of four held-out passages.
3. A synthesis from those four direct summaries.
4. A control synthesis from all four original passages.

The held-out battery contains 20 questions, including four source-absent questions. Question answers never enter the direct summaries. Gold never enters any model input. Merged synthesis receives direct summaries only. The full-source control receives original passages only.

The runner saves payloads, raw SSE streams, visible outputs, native statistics, first-visible delay, total wall time, cap status, and checkpoints. It bounds each request at 900 seconds and never retries an output cap. Completed fingerprints prevent duplicate requests on resumption. Changed payloads require a new output directory. Transport errors stop that profile because server cancellation cannot be assumed; confirm server idleness before another run. Failed checkpoints remain preserved.

A capped, empty, or failed direct summary blocks merged synthesis. An ordinary cap or empty response still permits the independent full-source control. Transport failure stops the profile. A terminal record is not an accuracy pass.

Portable visible-token rates use API total tokens minus reasoning tokens, when both exist. This may include control tokens. The Evo-specific runner additionally retokenizes visible text through the SDK and samples hardware telemetry. These measurements must not be silently pooled. The portable runner does not measure model-load time, GPU memory, power, or synthetic llama-bench throughput.

## Optional Linux scheduling

The direct runner works without systemd. `scripts/history_v2/after_job.py` is an optional Linux adapter. It waits for specified user services, verifies predecessor completion records, acquires a shared lock, then runs an explicit command. It makes no model-loading or browser-service changes.

```sh
python scripts/history_v2/after_job.py --help
```

An example user unit follows. Replace every example path and service name with your own values. The command assumes the chosen model will already be loaded when it starts; for a managed model queue, supply your own reviewed orchestration command.

```ini
[Unit]
Description=History accuracy after a speed benchmark
After=network-online.target

[Service]
Type=simple
WorkingDirectory=/absolute/path/hardware-benchmarks
ExecStart=/absolute/path/python /absolute/path/hardware-benchmarks/scripts/history_v2/after_job.py --wait-unit your-speed.service --speed-root /absolute/path/speed-results --lock /absolute/path/benchmark.lock --status /absolute/path/accuracy-wait-status.json -- /absolute/path/python /absolute/path/hardware-benchmarks/scripts/history_v2/runner.py run --profile gemma26-off --model-id history-gemma --output /absolute/path/accuracy-results

[Install]
WantedBy=default.target
```

The predecessor folder must contain `queue.json` with a `models` list of `id` objects, top-level `complete.json`, and each model's `complete.json` or `error.json`. Missing records produce an explicit blocked result. Add another `--wait-unit` for a separate boot-resume service, if used. The same shared lock must also be honored by the predecessor.

Save the unit under your user systemd directory, reload systemd, and enable the unit. User lingering is needed if it must continue after logout. Inspect both the unit's process state and its status JSON. An active service alone does not prove that generation started successfully.

## Source and reuse

Passages come from Charles Oman's public-domain *The Byzantine Empire*. The canonical scan has 396 physical PDF pages. Source SHA-256: `0187c4b558c683d5349b4cf427db4ca9713298f0e99660767d8dfbc2aa83c5f2`.

The fixture text preserves the original extraction and OCR noise. Matching Oman is a source-fidelity test, not certification of modern historical truth. Physical PDF page numbers differ from printed pages.

- [Canonical Internet Archive scan](https://archive.org/details/byzantineempire00omanrich)
- [Public-domain scan record and licensing](https://commons.wikimedia.org/wiki/File:The_Byzantine_Empire_(IA_byzantineempire00omanrich).pdf)
- [Project Gutenberg edition and rights information](https://www.gutenberg.org/ebooks/37756)
