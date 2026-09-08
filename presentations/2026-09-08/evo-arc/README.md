# Evo X3 and Windows Arc comparison

Six editable slides compare hardware capacity, synthetic generation speed, historical-workload timings, source fidelity, and model choices.

- [Editable PowerPoint](evo-arc-comparison.pptx)
- [Accessible companion and interpretation limits](overview.md)
- [Slide text, native table values, notes and pinned citations](source-data.json)
- [Build script](build.mjs)
- [Template provenance](build-provenance.json)

The deck retains Simple Light Mode reference slides 1, 5, 14 and 15. Three comparison tables are native PowerPoint tables. Qwen/Gemma reasoning OFF and GPT-OSS template medium appear on the timing slide. MTP and timing-definition differences remain explicit.

## Rebuilding

Use the Codex bundled Node runtime with `@oai/artifact-tool` available. This is not a claim that the package is publicly installable from npm. Place `build.mjs` and `source-data.json` together, and supply the selected Simple Light Mode `reference.pptx` through `TEMPLATE_PPTX`:

```sh
TEMPLATE_PPTX=/path/to/reference.pptx /path/to/bundled/node build.mjs
```

The script imports the reference, duplicates six slides, edits native content, writes `candidate.pptx`, and renders six PNGs. It does not run inference, download models, or require benchmark credentials. The template SHA-256 is recorded in `build-provenance.json`; the template package itself is not redistributed here.

Final delivery used the Presentations skill finalizer. It checked six slides, 12192000 × 6858000 EMU dimensions, Helvetica Neue / Helvetica Neue Medium from the reference, native tables on slides 3–5, package integrity, and Artifact Tool import. Each slide was inspected at full size. These checks do not establish native PowerPoint execution, independent human accuracy adjudication, or exact cross-hardware reproduction.

The data snapshot is pinned in `source-data.json`. Mac results are pending and excluded.
