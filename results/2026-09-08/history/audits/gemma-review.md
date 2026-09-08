# Gemma 26B source-fidelity review

Result: FAIL under the agreed provisional threshold. Completion and speed pass separately.

The accepted final request is book-final-summary-completion-retry. It contains 2,052 output tokens and ends normally. All 86 citation-attached claim units were compared with source text. Some units contain several closely related facts. The ledger distinguishes substantive errors from citation drift.

| Dimension | Score / 4 | Reason |
|---|---:|---|
| Factual accuracy | 2 | Changes the scope of the Nika death toll. |
| Chronology and causation | 2 | Reverses the source’s explanation of Gothic weakness. |
| Attribution | 2 | Some judgments are attributed; others become facts. |
| Citation support | 2 | Many citations point to adjacent or incomplete evidence. |
| Coverage | 2 | Reaches 1453 but omits Manzikert and leaves later coverage thin. |
| Uncertainty and limitations | 1 | Invents whole-book gaps from local chunk endings. |

Passing requires at least 3 in every dimension and no critical error. Scores are reviewer judgments, not a calibrated accuracy percentage.

The first 50-page summary was comparatively strong. It preserved the oracle as a legend and avoided Qwen's massacre conflation. In pages 201-250 it merges two escapes: Justinian first fled Cherson, then escaped the Khazars after killing their officers (PDF 204). The last group preserves the fall narrative but follows inconsistent imperial numbering without comment (PDF 351 and 356).

The final synthesis converts a correct chunk-level explanation of Gothic weakness into an explanation of Roman failure. Its final paragraph repeats limitations inherited from individual chunks. This shows information loss during synthesis, not proof of a hardware defect.

This audit tests the model against Oman, including his outdated terminology and interpretations. It does not certify current historical scholarship. OCR and illustrations impose additional limits.

Revision: the corrected ledger contains 14 material flags across 86 final units. The chronology objection to “simultaneously” was withdrawn because the 540 war can overlap the 542 plague. Leo’s missing reform details are source-supported. Neither withdrawn point contributes to this review. These are Codex-assisted source judgments, not independent human adjudication.
