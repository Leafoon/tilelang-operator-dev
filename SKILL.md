---
name: tilelang-operator-dev
description: Use when developing, adapting, explaining, or validating TileLang operators from a validated TileLang workspace and repo-local tilelang_knowledge delivery set, with MCP-backed retrieval and device-aware source fallback.
---

# TileLang Operator Dev

This skill is the long-lived engineering workflow for TileLang operator development. It must validate the active workspace, retrieve from `tilelang_knowledge/`, and only then generate code, explanations, or validation plans.

Default behavior is not "directly write code". Default behavior is: validate, retrieve, then generate.

## Scope

Use this skill for:

- GEMM, split-K GEMM, grouped GEMM, sparse GEMM, dequantized GEMM, and dynamic-shape GEMM
- Attention, flash attention, decode attention, MLA/GQA-style kernels
- Reductions, online softmax, RMSNorm, TopK
- Convolution-like kernels
- Elementwise and fusion kernels
- Device-aware TileLang target, layout, schedule, intrinsic, and validation planning

Do not use this skill for generic CUDA/Triton development unless the user explicitly wants a TileLang implementation.

## Mandatory MCP-First Validation

At the start of each operator task:

1. Call `inspect_tilelang_workspace` from `tilelang-operator-knowledge`.
2. Call `validate_knowledge_base` from `tilelang-operator-knowledge`.
3. If a device is supplied, call `normalize_device_profile`.

If MCP is unavailable, fall back to direct filesystem checks, but explicitly state that MCP validation was unavailable. The fallback must enforce the same hard-stop rules.

## Hard Stop Conditions

Stop immediately when:

- The active workspace is not a TileLang repository.
- `tilelang_knowledge/` is missing.
- Required delivery files are missing.
- JSON or JSONL parsing fails.
- The selected operator depends on evidence paths missing from the current repository.

When stopped, do not generate code and do not continue with inferred context.

Use this stop format:

```text
Cannot safely generate a TileLang operator yet.

Missing or invalid:
- <specific missing repository indicator, delivery file, parse error, or version mismatch>

Required fix:
- Place the TileLang repository at the active workspace root.
- Restore/generate tilelang_knowledge/ with retrieval_plan.md, capability_map.json,
  patterns.jsonl, usage_patterns.jsonl, apis.jsonl, source_chunks.jsonl,
  semantic_graph.json, semantic_graph.mmd, manifest.json, and README.md.
- Re-invoke the tilelang-operator-dev skill.
```

## Workspace Acceptance Criteria

A valid TileLang repository must include:

- `tilelang/__init__.py`
- `tilelang/language/__init__.py`
- `src/transform` or `src/op`
- at least one of `examples/`, `testing/`, or `docs/`

A valid delivery set must include:

- `tilelang_knowledge/retrieval_plan.md`
- `tilelang_knowledge/capability_map.json`
- `tilelang_knowledge/patterns.jsonl`
- `tilelang_knowledge/usage_patterns.jsonl`
- `tilelang_knowledge/apis.jsonl`
- `tilelang_knowledge/source_chunks.jsonl`
- `tilelang_knowledge/semantic_graph.json`
- `tilelang_knowledge/semantic_graph.mmd`
- `tilelang_knowledge/manifest.json`
- `tilelang_knowledge/README.md`

## Required Opening Status

When validation passes, begin with a short status:

- TileLang repository identified: `<path>`
- Knowledge delivery identified: `<path>/tilelang_knowledge`
- Workspace validation: passed
- Retrieval mode: MCP-backed layered knowledge first, source fallback only if needed

## Standard Workflow

1. Workspace validation: `inspect_tilelang_workspace`
2. Knowledge validation: `validate_knowledge_base`
3. Device profile normalization: `normalize_device_profile`
4. Capability search: `search_capabilities`
5. Pattern search: `search_patterns`
6. Usage search: `search_usage_patterns`
7. API confirmation: `lookup_apis`
8. Source fallback: `get_source_chunks`
9. Dependency tracing: `trace_semantic_graph`
10. Operator retrieval plan: `build_operator_retrieval_plan`
11. Implementation, explanation, or validation plan

Only step 11 may generate final operator code.

## Retrieval Order

Follow this order exactly:

1. `retrieval_plan.md`
2. `capability_map.json`
3. `patterns.jsonl`
4. `usage_patterns.jsonl`
5. `apis.jsonl`
6. `source_chunks.jsonl`
7. `semantic_graph.json` / `semantic_graph.mmd`
8. Original repository source, only as final fallback

Even after source fallback, do not ignore constraints already found in the delivery set. If repository source, delivery records, and user requirements conflict, report the conflict explicitly.

## Device Adaptation

Normalize device information before selecting target-specific patterns or intrinsics:

- NVIDIA A100 or Ampere: likely `cuda -arch=sm_80` when confirmed.
- NVIDIA H100 or Hopper: likely `cuda -arch=sm_90` when confirmed.
- NVIDIA B100 or Blackwell: likely `cuda -arch=sm_100a` or exact repo-supported Blackwell target when confirmed.
- AMD MI300X, MI350, or CDNA: `hip -mcpu=gfxXXX` only when exact gfx arch is known.
- CPU: `llvm` or `c`.
- Apple Silicon: `metal`.
- WebGPU: `webgpu`.

If exact architecture is unknown, mark confidence lower and do not invent `sm_XX` or `gfxXXX`.

Use these fields from delivery records:

- `device_adaptation`
- `device_strategy`
- `device_execution_notes`
- `device_notes`

Before recommending WGMMA, TCGEN05, TMA, `cp.async`, MFMA, LDS, TMEM, `cluster_dims`, or `is_cpu=True`, verify the relevant delivery field and source/API evidence.

## Retrieval Trace Required Before Code

Before generating code, output:

- Workspace status
- Device profile
- Selected `capability_id`
- Selected `pattern_id`
- Selected `usage_id`
- API symbols and visibility
- Source chunk IDs if used
- Confidence and limitations

## Implementation Style

Generated TileLang code should follow repository style:

- `import tilelang`
- `import tilelang.language as T`
- `@tilelang.jit` or `@tilelang.jit(out_idx=[...])`
- `@T.prim_func`
- `T.Tensor`
- `with T.Kernel(...)`
- `T.alloc_shared`, `T.alloc_fragment`, `T.alloc_local`, `T.alloc_var`
- `T.copy`, `T.Pipelined`, `T.Parallel`
- `T.gemm`, `T.gemm_sp`, `T.reduce_*`, or other APIs only after `lookup_apis`

Prefer adapting the closest retrieved pattern over inventing a new structure.

## Validation Plan

When validation is requested or needed:

- Use retrieved usage patterns for compile/run/compare/profile order.
- Create tensors on the target-matching runtime device.
- Use `torch.testing.assert_close` or `Profiler.assert_allclose` when appropriate.
- Use `kernel.get_kernel_source()` for lowering/codegen inspection.
- Use `kernel.get_profiler().do_bench(...)` only with a compatible backend.
- For dynamic shapes, provide concrete `input_tensors` when the usage record requires it.

Do not claim validation passed unless a check actually ran and passed.

## Output Format

Default structure:

1. **Workspace Check**
2. **Operator Intent**
3. **Device Profile**
4. **Retrieval Trace**
5. **Selected Pattern**
6. **API Contract**
7. **Implementation**
8. **Validation Plan**
9. **Risks / Confidence**

For small explanatory questions, keep the answer shorter but still state whether workspace validation passed and which delivery layers were used.

## Follow-Up Behavior

For follow-up requests:

- Continue from the previous retrieval trace when the operator and device are unchanged.
- Re-run device normalization and device-aware pattern search when the user changes hardware.
- Re-run capability and pattern retrieval when the operator family changes.
- Do not rebuild from scratch unless the user changes the scope enough to invalidate the prior trace.

## Confidence Rules

- High confidence: source- or doc-backed in the current workspace.
- Medium confidence: example/test-backed but not fully documented.
- Low confidence: inferred, target-specific, version-sensitive, or weakly covered.

Internal APIs must not be presented as public unless `apis.jsonl` marks them public/exported or source evidence justifies controlled use.

## Boundaries

- Do not modify TileLang repository source unless the user asks for code changes.
- Do not regenerate or modify `tilelang_knowledge/` during normal operator development.
- Do not copy `tilelang_knowledge/` into the plugin.
- MCP tools do not generate final operator code; they only validate, search, normalize, and return evidence.
- Do not bypass layered retrieval because source files are nearby.
- Do not continue after a hard precondition failure.
