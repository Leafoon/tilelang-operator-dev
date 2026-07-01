---
name: tilelang-operator-dev
description: Use when developing, adapting, explaining, or validating TileLang operators in Claude Code. Supports independent operator workspaces, MCP-backed TileLang knowledge retrieval, bundled or workspace-local tilelang_knowledge, device-aware planning, implementation guidance, troubleshooting, and code validation.
---

# TileLang Operator Dev

Use this skill for TileLang operator development in Claude Code. Validate the workspace, validate the knowledge base, retrieve evidence, and only then generate explanations, implementation plans, operator code, or validation plans.

## Workspace Model

Support both layouts:

- **Single-workspace mode**: the active Claude Code workspace is the TileLang source repository.
- **Dual-workspace mode**: the active Claude Code workspace contains custom operators, while the TileLang source repository lives elsewhere, commonly as a sibling directory.

Recommended local layout:

```text
<workspace-root>/
├── tilelang-operator-dev/   # this skill and MCP server
├── tilelang/                # official TileLang source repository
└── my-operators/            # independent Claude Code operator workspace
```

In dual-workspace mode, the active workspace does not need to be the TileLang source repository. The MCP server resolves TileLang source from `tilelang_source_path`, `TILELANG_SOURCE_PATH`, auto-detected sibling/parent `tilelang/`, or the active workspace as a final fallback.

The knowledge base resolves from workspace-local `tilelang_knowledge/` first, then bundled `resources/tilelang_knowledge/` from the `tilelang-operator-dev` repository. A complete delivery set includes retrieval, capability, pattern, usage, API, source chunk, semantic graph, manifest, README, and troubleshooting records.

## Mandatory MCP-First Validation

At the start of each operator task:

1. Call `inspect_tilelang_workspace` from `tilelang-operator-knowledge`.
2. Call `validate_knowledge_base` from `tilelang-operator-knowledge`.
3. If a device is supplied, call `normalize_device_profile`.

If MCP is unavailable, fall back to direct filesystem checks and explicitly state that MCP validation was unavailable.

## Hard Stops

Stop immediately when no valid TileLang source repository can be resolved, no valid workspace-local or bundled knowledge base is available, required delivery files are missing, JSON/JSONL parsing fails, or selected evidence paths are missing from the resolved source repository.

Do not generate code after a hard stop.

## Workflow

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

Only step 11 may generate final operator code. For a guided flow, use `operator_development_wizard`.

## Device Rules

Normalize device information before selecting target-specific patterns or intrinsics. Do not invent `sm_XX` or `gfxXXX`. Before recommending WGMMA, TCGEN05, TMA, `cp.async`, MFMA, LDS, TMEM, `cluster_dims`, or `is_cpu=True`, verify the relevant delivery field and source/API evidence.

## Retrieval Trace Required Before Code

Before generating code, output workspace status, device profile, selected `capability_id`, selected `pattern_id`, selected `usage_id`, API symbols and visibility, source chunk IDs if used, confidence, and limitations.

## Implementation Style

Prefer adapting the closest retrieved pattern. Generated TileLang code should use repository style: `import tilelang`, `import tilelang.language as T`, `@tilelang.jit`, `@T.prim_func`, `T.Tensor`, `with T.Kernel(...)`, `T.alloc_shared`, `T.alloc_fragment`, `T.copy`, `T.Pipelined`, `T.Parallel`, and APIs confirmed by `lookup_apis`.

Do not claim validation passed unless a check actually ran and passed.
