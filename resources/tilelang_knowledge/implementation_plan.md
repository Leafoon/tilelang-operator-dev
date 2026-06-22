# TileLang Knowledge Delivery Implementation Plan

## 1. Project Goal

This knowledge delivery set is built for later TileLang operator development, not for a general repository summary. The expected downstream scenarios are:

- Generate or adapt GEMM-like kernels.
- Generate attention-like kernels.
- Build reduction, convolution, elementwise, and fused operators.
- Locate the right TileLang DSL symbols, runtime helpers, examples, tests, and lowering constraints before writing code.
- Fall back to relevant source blocks only when the higher-level knowledge layers are insufficient.

Directly relying on source code is too slow and too fragile for later operator generation because the repository contains Python DSL code, C++ lowering passes, examples, tests, benchmarks, documentation, and runtime/build support with different levels of relevance. The delivery set will therefore be layered:

1. High-level capability map for fast operator-domain routing.
2. Pattern and usage layers for reusable operator organization and call order.
3. API/symbol layer for precise symbol lookup.
4. Source chunk layer for evidence-backed fallback.
5. Semantic graph layer for dependency, exposure, and concept tracing.

The primary design constraint is that every file must help a future agent answer: "How should I build this TileLang operator, which existing pattern should I reuse, which APIs are valid, and where do I inspect source if uncertain?"

## 2. Phased Plan

### Phase 1: Repository Scan And Scope Confirmation

- Input:
  - Repository root.
  - `tilelang/`, `src/`, `examples/`, `testing/` or `tests/`, `benchmark*`, `docs/`, `README*`, build metadata, and package entry points.
- Actions:
  - Enumerate key directories and file counts.
  - Identify Python public modules and C++ backend/lowering modules.
  - Identify examples, tests, and benchmark files most relevant to operator development.
  - Capture repository metadata for `manifest.json`.
- Output files:
  - `manifest.json` metadata fields.
  - Inputs for all later extraction phases.
- Risks:
  - Directory names may differ from the expected names.
  - Some examples may be generated, archived, or experimental.
- Mitigation:
  - Use actual filesystem discovery rather than fixed assumptions.
  - Mark uncertain or inferred coverage with notes and confidence.

### Phase 2: API And Symbol Extraction

- Input:
  - Python modules under TileLang package roots.
  - Important C++ registration/lowering files under `src/`.
  - Package `__init__.py` files and export surfaces.
- Actions:
  - Parse Python AST for classes, functions, methods, signatures, docstrings, parents, and line ranges.
  - Grep C++ files for pass registrations, key functions, and exposed symbols where useful.
  - Classify visibility as `public`, `exported`, `internal`, or `test_only`.
  - Attach operator relevance and evidence paths/lines.
- Output files:
  - `apis.jsonl`.
  - API nodes/edges for `semantic_graph.json`.
- Risks:
  - Dynamic exports or FFI-bound symbols may not be fully visible from Python AST.
  - Some important C++ functionality is not easily expressible as public APIs.
- Mitigation:
  - Include evidence from `__init__.py`, decorators, import sites, and source chunks.
  - Use conservative visibility labels and confidence values.

### Phase 3: Pattern And Usage Extraction

- Input:
  - `examples/`, `testing/` or `tests/`, `benchmark*`, `docs/`, tutorials, and README files.
- Actions:
  - Identify operator families such as GEMM, attention, reduction, convolution, elementwise, fusion, copy/memory movement, and tuning/benchmark flows.
  - Extract pattern-level structure: inputs, outputs, memory flow, control flow, required symbols, optional symbols, and reuse guidance.
  - Extract usage-level call sequences: define primitive, annotate/layout, compile/lower, execute, compare/benchmark.
- Output files:
  - `patterns.jsonl`.
  - `usage_patterns.jsonl`.
  - Pattern/usage source chunk candidates.
- Risks:
  - Tests may focus on compiler behavior rather than minimal user-facing examples.
  - Examples may depend on hardware-specific features.
- Mitigation:
  - Prefer examples for reusable operator patterns, tests for edge cases and failure modes, and benchmarks for performance/tuning patterns.
  - Record prerequisites and failure modes explicitly.

### Phase 4: Capability Map And Semantic Graph Construction

- Input:
  - Outputs from API extraction, pattern extraction, usage extraction, and source scan.
- Actions:
  - Build capability entries from the operator developer viewpoint:
    - `kernel_construction`
    - `memory_movement`
    - `tiling_and_schedule`
    - `pipelining`
    - `tensor_intrinsics`
    - `reductions`
    - `gemm_like_patterns`
    - `attention_like_patterns`
    - `convolution_like_patterns`
    - `elementwise_and_fusion_patterns`
    - `lowering_or_codegen_related_components`
    - `testing_and_validation_support`
  - Connect capabilities to symbols, modules, patterns, and source evidence.
  - Build machine-readable graph nodes and edges.
  - Build a smaller Mermaid overview graph for human orientation.
- Output files:
  - `capability_map.json`.
  - `semantic_graph.json`.
  - `semantic_graph.mmd`.
- Risks:
  - Capabilities can overlap, especially scheduling, memory movement, and tensor intrinsics.
  - Some graph edges may be inferred from imports or examples rather than direct calls.
- Mitigation:
  - Use explicit `edge_type`, `evidence`, and confidence where practical.
  - Prefer multiple small capability entries over one vague global category.

### Phase 5: Source Fallback Layer Construction

- Input:
  - Core source files, API extraction results, pattern/usage evidence, and critical docs.
- Actions:
  - Select meaningful source chunks rather than mechanically chunking the entire repository.
  - Include chunks for DSL entry points, layout abstractions, JIT/lowering flow, language primitives, examples, tests, and key C++ passes.
  - Summarize why each chunk matters for operator development.
- Output files:
  - `source_chunks.jsonl`.
- Risks:
  - Too many chunks reduce retrieval precision.
  - Too few chunks force future agents back to whole-repo scans.
- Mitigation:
  - Prioritize source chunks tied to capabilities, patterns, usage flows, and important APIs.
  - Keep evidence line ranges compact enough for direct source fallback.

### Phase 6: Delivery Validation And Summary

- Input:
  - All generated delivery files.
- Actions:
  - Validate JSON and JSONL syntax.
  - Check every required file exists under `tilelang_knowledge/`.
  - Check key cross references are plausible.
  - Write human-facing `README.md` and executable `retrieval_plan.md`.
- Output files:
  - `README.md`.
  - `retrieval_plan.md`.
  - Final validated set.
- Risks:
  - Cross references may drift if files are generated independently.
  - Some inferred knowledge may look more certain than the evidence supports.
- Mitigation:
  - Use stable IDs and explicit evidence fields.
  - Add notes for incomplete or inference-based areas.

## 3. Delivery Dependencies

- `implementation_plan.md` is created first and controls the remaining work.
- `manifest.json` depends on Phase 1 repository scan.
- `apis.jsonl` depends on Phase 2 symbol extraction.
- `patterns.jsonl` depends on Phase 3 example/test/benchmark/doc analysis.
- `usage_patterns.jsonl` depends on Phase 3 usage-flow extraction.
- `capability_map.json` depends on `apis.jsonl`, `patterns.jsonl`, `usage_patterns.jsonl`, and source scan notes.
- `semantic_graph.json` depends on APIs, capabilities, patterns, usage flows, imports, and selected source edges.
- `semantic_graph.mmd` depends on the most important nodes and edges from `semantic_graph.json`.
- `source_chunks.jsonl` depends on the evidence needed by capabilities, APIs, patterns, and usage flows.
- `README.md` and `retrieval_plan.md` are written after the main content structure is known, but must remain consistent with this plan.

This dependency order supports layered retrieval because high-level routing must be stable before a future agent descends into examples, APIs, and source chunks.

## 4. Retrieval Strategy For Future Operator Development

Recommended retrieval path:

1. Read `retrieval_plan.md` for the operational workflow.
2. Query `capability_map.json` to classify the requested operator into capability domains. Use this when deciding whether the task is GEMM-like, attention-like, reduction-like, memory-movement-heavy, schedule-heavy, or validation-focused.
3. Query `patterns.jsonl` for a reusable operator structure. Use this when deciding how to organize loops, tiling, memory flow, compute, and writeback.
4. Query `usage_patterns.jsonl` for minimum viable call order. Use this when implementing code around the kernel: creation, compilation, invocation, comparison, benchmarking, and tuning.
5. Query `apis.jsonl` for exact symbol names, signatures, visibility, modules, and line ranges. Use this before calling a DSL primitive or internal helper.
6. Query `source_chunks.jsonl` only when API and pattern layers are insufficient, when behavior is ambiguous, or when hardware/lowering constraints need direct source evidence.
7. Query `semantic_graph.json` or `semantic_graph.mmd` when tracing dependencies, imports, exposes relationships, capability-to-pattern links, or lowering/codegen paths.

The fallback rule is: never start from broad source scanning for a later operator request unless the delivery files cannot answer the routing, pattern, usage, or API question.

## 5. Coverage Priorities

Highest priority modules and directories:

- Public TileLang Python package roots and package export files.
- Core language/DSL construction APIs.
- JIT, compile, lowering, layout, and runtime-facing modules.
- `examples/` operator implementations.
- Tests that demonstrate real operator construction or DSL usage.
- Benchmarks showing performance-oriented schedules and tuning.
- Docs and README files that define intended user workflows.
- C++ lowering/transform files only where they explain constraints that affect operator authoring.

Highest priority patterns:

- GEMM-like patterns, including tiled matrix multiplication and tensor-core variants.
- Attention-like patterns, especially flash-attention-style memory and reduction organization.
- Reduction patterns, including block/thread reductions and allreduce-like helpers.
- Convolution-like patterns where present.
- Elementwise/fusion patterns.
- Pipelining and asynchronous memory movement.
- Tensor intrinsic and layout mapping usage.
- Compile/run/validate/benchmark loops.

Quality must be strongest for:

- `implementation_plan.md`
- `capability_map.json`
- `patterns.jsonl`
- `usage_patterns.jsonl`
- `apis.jsonl`
- `source_chunks.jsonl`

## 6. Risks And Limits

- Some conclusions may be inferred from examples or test naming rather than direct docs. These records must use lower confidence and explain the inference.
- Dynamic Python behavior, TVM FFI registration, and C++ pass registration may hide symbols from static extraction.
- Hardware-specific features may require CUDA architecture, backend, or dependency assumptions that cannot be validated from static reading alone.
- If examples/tests are sparse for a pattern, source and docs will be used as supplemental evidence, and the record will state the coverage gap.
- Confidence values should be high only when source evidence directly supports the claim. Inferred edges, inferred operator families, and undocumented internal symbols should have medium or low confidence.

## 7. Execution Order

1. Create `tilelang_knowledge/`.
2. Write this `implementation_plan.md`.
3. Run repository scans and symbol extraction.
4. Generate `manifest.json`, `apis.jsonl`, `patterns.jsonl`, `usage_patterns.jsonl`, `source_chunks.jsonl`, `capability_map.json`, `semantic_graph.json`, and `semantic_graph.mmd`.
5. Generate `README.md` and `retrieval_plan.md`.
6. Validate JSON/JSONL and required file presence.
7. Provide a concise final summary with coverage and known gaps.
