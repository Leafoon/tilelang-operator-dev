# TileLang Operator Development Knowledge Base

This directory is a layered knowledge base for later TileLang operator development. It is not a general repository summary. Future agents should consult these delivery files before scanning the source tree directly.

## What This Covers

- Core TileLang DSL construction: `@tilelang.jit`, `T.prim_func`, `T.Tensor`, `T.Kernel`.
- Memory movement and staging: `T.copy`, `T.async_copy`, `T.tma_copy`, shared/local/fragment allocation.
- Scheduling and layout: `T.Parallel`, `T.Pipelined`, layout annotations, swizzle and occupancy hints.
- Tensor intrinsics: `T.gemm`, WGMMA, TCGEN05, sparse GEMM variants, `GemmWarpPolicy`.
- Reusable operator patterns: GEMM, split-K, sparse/dequantized/grouped GEMM, attention/decode, reductions/softmax/RMSNorm, convolution, elementwise/fusion, top-k, dynamic shape, autotuning.
- Validation and fallback: profiler, generated source inspection, transform/lowering source chunks.
- Device-aware development: target selection, vendor/model notes, architecture-specific intrinsic limits, and per-device scheduling/memory remarks.

## Files

- `implementation_plan.md`: engineering plan followed to create this delivery set.
- `manifest.json`: repository metadata, scan roots, file counts, and output list.
- `retrieval_plan.md`: step-by-step retrieval procedure for future operator tasks.
- `capability_map.json`: first-layer capability routing map from an operator-development perspective.
- `patterns.jsonl`: reusable operator/kernel organization patterns.
- `usage_patterns.jsonl`: minimal call sequences, prerequisites, and failure modes.
- `apis.jsonl`: public and important internal symbols with signatures, line ranges, visibility, and evidence.
- `source_chunks.jsonl`: selected source/doc/backend chunks for final fallback retrieval.
- `semantic_graph.json`: machine-readable concept/symbol/pattern graph.
- `semantic_graph.mmd`: compact Mermaid graph for human orientation.

## Device-Aware Fields

- `capability_map.json`: each capability includes `device_adaptation`.
- `patterns.jsonl`: each pattern includes `device_strategy`.
- `usage_patterns.jsonl`: each usage record includes `device_execution_notes`.
- `source_chunks.jsonl`: each chunk includes `device_notes`.

When a user provides a vendor/model, resolve the target first, for example `cuda -arch=sm_90`, `hip -mcpu=gfx950`, `llvm`, `c`, `metal`, or `webgpu`, then follow the normal retrieval order.

## Recommended Retrieval Order

1. Read `retrieval_plan.md`.
2. Use `capability_map.json` to classify the operator request.
3. Use `patterns.jsonl` to find similar operator structure and target-specific strategy.
4. Use `usage_patterns.jsonl` to recover the correct call order, validation flow, and device-specific execution notes.
5. Use `apis.jsonl` to confirm signatures, visibility, modules, and line ranges.
6. Use `source_chunks.jsonl` only when the previous layers are ambiguous or incomplete, especially for architecture-specific intrinsic or memory behavior.
7. Use `semantic_graph.json` or `semantic_graph.mmd` when tracing dependencies, concept relationships, or device-family links.

Do not start a future operator-generation task by scanning the whole source tree unless these layers fail to answer the question.

## Confidence And Evidence

Every major record contains evidence paths and confidence. High-confidence records are directly supported by source or docs. Medium/low-confidence records are usually inferred from examples, tests, filenames, or transform naming and should be verified through `source_chunks.jsonl` or the original source when correctness depends on them.
