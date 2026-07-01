---
name: tilelang-operator-dev
description: Use when developing, adapting, explaining, or validating TileLang operators in Claude Code. Supports independent operator workspaces, MCP-backed TileLang knowledge retrieval, bundled or workspace-local tilelang_knowledge, device-aware planning, implementation guidance, troubleshooting, and code validation.
---

# TileLang Operator Dev

Use this skill for TileLang operator development in Claude Code. The default workflow is:

1. Validate the operator workspace and TileLang source repository.
2. Validate the knowledge base.
3. Retrieve capability, pattern, usage, API, and source evidence.
4. Generate explanations, implementation plans, operator code, or validation plans.

Do not skip validation and retrieval before generating operator code.

## Scope

Use this skill for:

- GEMM, split-K GEMM, grouped GEMM, sparse GEMM, dequantized GEMM, and dynamic-shape GEMM
- Attention, flash attention, decode attention, MLA/GQA-style kernels
- Reductions, online softmax, RMSNorm, TopK
- Convolution-like kernels
- Elementwise and fusion kernels
- Device-aware TileLang target, layout, schedule, intrinsic, validation, and troubleshooting work

Do not use this skill for generic CUDA or Triton development unless the user explicitly asks for a TileLang implementation.

## Workspace Model

Support both layouts:

- **Single-workspace mode**: the active Claude Code workspace is the TileLang source repository.
- **Dual-workspace mode**: the active Claude Code workspace contains custom operators, while the TileLang source repository lives elsewhere, commonly as a sibling directory.

Recommended local layout:

```text
/temp/
├── tilelang-operator-dev/   # this skill and MCP server
├── tilelang/                # official TileLang source repository
└── my-operators/            # independent Claude Code operator workspace
```

In dual-workspace mode, the active workspace does not need to be the TileLang source repository. The MCP server resolves TileLang source in this order:

1. Explicit `tilelang_source_path` tool argument
2. `TILELANG_SOURCE_PATH` environment variable
3. Auto-detected sibling or parent `tilelang/` directory
4. Active workspace as a backward-compatible fallback

The knowledge base resolves in this order:

1. Workspace-local `tilelang_knowledge/`, if present and complete enough
2. Bundled `resources/tilelang_knowledge/` from the `tilelang-operator-dev` repository

## Mandatory MCP-First Validation

At the start of each operator task:

1. Call `inspect_tilelang_workspace` from `tilelang-operator-knowledge`.
2. Call `validate_knowledge_base` from `tilelang-operator-knowledge`.
3. If a device is supplied, call `normalize_device_profile`.

If MCP is unavailable, fall back to direct filesystem checks and explicitly state that MCP validation was unavailable. The fallback must enforce the same hard-stop rules.

## Hard Stop Conditions

Stop immediately when:

- No valid TileLang source repository can be resolved.
- Neither a valid workspace-local nor bundled `tilelang_knowledge` delivery set is available.
- Required delivery files are missing.
- JSON or JSONL parsing fails.
- The selected operator depends on evidence paths missing from the resolved TileLang source repository.

When stopped, do not generate code and do not continue with inferred context.

Use this stop format:

```text
Cannot safely generate a TileLang operator yet.

Missing or invalid:
- <specific missing repository indicator, delivery file, parse error, or version mismatch>

Required fix:
- Ensure a TileLang source repository is available, for example /temp/tilelang.
- Ensure the Claude Code workspace can load tilelang-operator-knowledge from tilelang-operator-dev.
- Restore workspace-local tilelang_knowledge/ or bundled resources/tilelang_knowledge/.
- Re-invoke the tilelang-operator-dev skill.
```

## Acceptance Criteria

A valid TileLang source repository must include:

- `tilelang/__init__.py`
- `tilelang/language/__init__.py`
- `src/transform` or `src/op`
- at least one of `examples/`, `testing/`, or `docs/`

A valid delivery set must include:

- `retrieval_plan.md`
- `capability_map.json`
- `patterns.jsonl`
- `usage_patterns.jsonl`
- `apis.jsonl`
- `source_chunks.jsonl`
- `semantic_graph.json`
- `semantic_graph.mmd`
- `manifest.json`
- `README.md`

## Required Opening Status

When validation passes, begin with a short status:

- Operator workspace identified: `<path>`
- TileLang source identified: `<path>`
- Knowledge delivery identified: `<path>`
- Workspace mode: `single` or `dual`
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
12. Code quality validation: `validate_operator_code`
13. Troubleshooting: `search_troubleshooting` when errors occur

Only step 11 may generate final operator code.

For a guided experience, use `operator_development_wizard`.

## Retrieval Order

Follow this order:

1. `retrieval_plan.md`
2. `capability_map.json`
3. `patterns.jsonl`
4. `usage_patterns.jsonl`
5. `apis.jsonl`
6. `source_chunks.jsonl`
7. `semantic_graph.json` or `semantic_graph.mmd`
8. Original TileLang repository source, only as a final fallback

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

- Use retrieved usage patterns for compile, run, compare, and profile order.
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

- High confidence: source- or doc-backed in the current resolved TileLang source repository.
- Medium confidence: example/test-backed but not fully documented.
- Low confidence: inferred, target-specific, version-sensitive, or weakly covered.

Internal APIs must not be presented as public unless `apis.jsonl` marks them public/exported or source evidence justifies controlled use.

## Boundaries

- Do not modify TileLang repository source unless the user asks for code changes.
- Do not regenerate or modify `tilelang_knowledge/` during normal operator development.
- Do not copy the full `tilelang-operator-dev` repository into an operator workspace.
- MCP tools do not generate final operator code; they only validate, search, normalize, and return evidence.
- Do not bypass layered retrieval because source files are nearby.
- Do not continue after a hard precondition failure.
