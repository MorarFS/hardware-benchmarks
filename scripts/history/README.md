# Adapted original full-book workflow

These Unix-oriented helpers reconstruct the original history-summary pipeline. Python 3.11+, LM Studio's native API, the `lms` CLI, and the pinned dependencies in `requirements.txt` are required. `fcntl` makes this wrapper unsuitable for Windows without adaptation. The new history-v2 runner is separately cross-platform.

Install the requirements in a dedicated virtual environment. Use the published `results/2026-09-08/history/source/` folder for the exact canonical input. `source.json` records verified provenance; `pages.json` supplies the original text and per-page hashes. Re-extraction is optional and may differ. `source.py` additionally requires English Tesseract data at the selected work directory's `tessdata/eng.traineddata` when OCR is needed.

Inspect `run.py --help`. Choose a model identifier from `configs/history/original-configurations.json` or `reasoning-configurations.json`, its exact installed GGUF, and its verified hash. The script refuses an unrelated loaded model or active inference. Use a dedicated local server and select the intended runtime before running. It does not install models, select a backend, or restore unrelated serving configuration.

Example structure, replacing the uppercase placeholders:

```sh
python scripts/history/run.py --work-dir work/original-history --config configs/history/original-configurations.json --source-dir results/2026-09-08/history/source --mode original --model CONFIG_MODEL_IDENTIFIER --model-file /path/to/verified.gguf --model-sha256 EXPECTED_SHA256
```

Use `--mode reasoning` with the reasoning configuration. Exact sampler limitations, context choices, retries, caps, and failed native fields are documented in the historical report. The source-level adaptive retry policy is part of this older workflow and differs from the fixed history-v2 pilot.

The adapted wrapper's syntax and command help were checked. It was not used to rerun the published dataset. The archived original scripts under the result folder retain historical execution logic with private-path placeholders. Their original hashes and the public sanitized-file manifest are distinct.
