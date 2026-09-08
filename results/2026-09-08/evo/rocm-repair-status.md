# ROCm repair: measured boundary and current tests

Status: AMD’s isolated patched build resolves the observed Qwen repetition failure in two short and two long trials. Gemma also completed two short and two long trials without repetition or caps. This is a runtime workaround, not a general source-accuracy certification.

The identical Qwen3-8B Q4_K_M weights work as ordinary prose on Vulkan. Installed LM Studio HIP 2.33.0 produced repetitive, capped output on all three short and three 50-page requests. Gemma26 HIP similarly failed all three 50-page requests, while its short responses remained readable. These are generation failures, not reported GPU crashes or context-limit rejections.

The official upstream b10852 server, commit 050dde50c, reproduced a long failure outside LM Studio. It used one slot, context 32,768, full GPU layer offload, FP16 KV, flash attention ON, logical and physical batches 512, and identical weights. Thus the failure is not confined to LM Studio’s chat interface or four-slot configuration. The diagnostic source exceeds 15,000 tokens and crosses many 512-token processing boundaries.

| Diagnostic | Short result | Long result | Interpretation |
|---|---|---|---|
| Upstream b10852 HIP, original settings | Readable, but omitted requested citations and showed suspicious source carryover | Repeated output, 512-token cap; failed record retrieval | Standalone failure reproduced |
| Same build, GGML_CUDA_NO_PINNED=1 | No inference | No inference | Startup timed out after 120 seconds; terminated and restored idle model |
| Same build, --no-op-offload | Failed record retrieval | Both long trials repeated and capped | Not a validated workaround |
| Same build, flash attention OFF | Wrong repeated code and invented prose | Timed out after 90 seconds; terminated | Not a validated workaround |
| Upstream b10852 with AMD’s newer ROCm libraries | Failed record retrieval | Repetitive output and token cap | Updating libraries alone did not resolve the failure |
| AMD gfx11 release, 6 September | Two readable responses; both record codes correct | Two readable responses; both codes correct; neither capped | Qwen repetition workaround validated on this bounded battery |

The proposed memory-handling explanation remains a hypothesis for this machine. An upstream report describes gfx1151 corruption involving direct access to pinned host buffers. AMD’s source excludes gfx1151 from that access path while retaining integrated-GPU classification. This differs from disabling pinned allocation entirely. [Issue 28211](https://github.com/ggml-org/llama.cpp/issues/28211), [specific source change](https://github.com/ggml-org/llama.cpp/commit/865374bbea0a65966c5d1a79c0c1f73ac8f1bfb4).

The candidate is AMD-Ecosystem’s `gfx11-rocm-nightly-20260906`, source commit `03d2068a1a2a8b9c9eb7684da8b275c13e9f4c56`. The published archive is 741,558,014 bytes, expected SHA-256 `57f0cf14679dbfc920204abf2f4e73e2f43503bd7f7fc40811e41d5a6bc06f9f`. The downloaded archive matched this checksum at 09:04:40 UTC. [Release](https://github.com/AMD-Ecosystem/llama.cpp/releases/tag/gfx11-rocm-nightly-20260906).

A repair requires repeated readable short and long outputs, correct requested facts, and retained qualifications. Retrieving two test codes alone does not pass. No driver, kernel, BIOS, or OS replacement has occurred. The new accuracy pilot and its audit remain separate from these repair tests.

## Candidate result, 09:07 UTC

The fixed-build Qwen long requests each processed 15,819 tokens, crossing many 512-token boundaries. Both completed in about 25.2 seconds and produced 199 native output tokens. Native decode was 26.14–26.15 tokens/s, below the requested above-40 target at this depth. Short native decode was 41.74–41.83 tokens/s. These diagnostics were nonstreaming, so these figures are native decode, not measured visible-phase timing. They are not the laptop-matched synthetic test.

Codex-assisted source inspection found ordinary summaries related to the supplied source. Both long outputs describe Byzantium’s founding and strategic position, Constantine’s capital, and the author’s introductory framing. They omit exact requested page citations and compress coverage. One short output goes beyond the two supplied pages when describing troops as quelling disturbances. Thus basic generation and retrieval now work, while factual and citation evaluation remains separate.

The AMD build differs from stock upstream in more than the cited patch. Comparing stock upstream against AMD with the same newer libraries narrows the working change to the backend build, but does not isolate one source commit experimentally. No replacement of installed LM Studio, system drivers, or OS has occurred. The verified package and launch settings provide a reversible standalone path.

## Integration and further failed control

A separate local browser-provider route was validated using the patched AMD build. Its configuration used context 32,768, one slot, full GPU offload, F16 KV, flash attention, and reasoning OFF. Private connection settings, keys, and provider backups are excluded from this repository. This route did not replace LM Studio's installed HIP runtime or its default Vulkan provider.

Gemma's two long diagnostic responses were readable and page-cited, with native decode near 40.56 tokens/s. This does not certify every claim or citation. An additional stock b10852 `--no-host` test failed both short record checks and both long requests. Its [raw evidence](raw/rocm-no-host/) remains available alongside the [other failed controls](raw/rocm-diagnostic-settings/).
