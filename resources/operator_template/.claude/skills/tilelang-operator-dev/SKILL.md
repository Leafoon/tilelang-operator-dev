---
name: tilelang-operator-dev
description: Use when developing, adapting, explaining, or validating TileLang operators in Claude Code. Supports independent operator workspaces, MCP-backed TileLang knowledge retrieval, bundled or workspace-local tilelang_knowledge, device-aware planning, implementation guidance, troubleshooting, and code validation.
---

# TileLang Operator Dev

Use this skill for TileLang operator work in Claude Code. Validate the workspace, validate the knowledge base, retrieve evidence, then generate explanations, implementation plans, operator code, or validation plans.

## Workspace Model

Support both layouts:

- **Single-workspace mode**: the active Claude Code workspace is the TileLang source repository.
- **Dual-workspace mode**: the active Claude Code workspace contains custom operators, while the TileLang source repository lives elsewhere.

Recommended sibling layout:

```text
<workspace-root>/
├── tilelang-operator-dev/   # this skill and MCP server
├── tilelang/                # official TileLang source repository
└── my-operators/            # independent Claude Code operator workspace
```

The MCP server resolves TileLang source from `tilelang_source_path`, `TILELANG_SOURCE_PATH`, an auto-detected sibling or parent `tilelang/`, then the active workspace as a final fallback.

The knowledge base resolves from a complete workspace-local `tilelang_knowledge/` first, then bundled `resources/tilelang_knowledge/` from `tilelang-operator-dev`. Do not create or modify workspace-local knowledge during normal operator development; use it only for intentional complete overrides.

## Required MCP Workflow

At the start of each operator task:

1. Call `inspect_tilelang_workspace`.
2. Call `validate_knowledge_base`.
3. If hardware is supplied, call `normalize_device_profile`.
4. Retrieve capabilities, patterns, usage records, APIs, and source chunks.
5. Call `build_operator_retrieval_plan`.
6. Generate code, explanations, or validation plans only after the retrieval trace is available.
7. Validate generated code with `validate_operator_code`.
8. Use `search_troubleshooting` for compile, runtime, correctness, or performance errors.

For guided work, call `operator_development_wizard`.

## Hard Stops

Do not generate code when:

- No valid TileLang source repository can be resolved.
- No valid workspace-local or bundled knowledge base is available.
- Required delivery files are missing.
- JSON or JSONL parsing fails.
- Selected evidence paths are missing from the resolved TileLang source repository.

If stopped, state the missing repository, delivery file, parse error, or evidence path and ask the user to fix that condition before continuing.

## Retrieval Trace

Before generating operator code, report:

- Operator workspace, TileLang source, and knowledge delivery path
- Workspace mode and MCP retrieval status
- Device profile and target confidence
- Selected `capability_id`, `pattern_id`, and `usage_id`
- API symbols and visibility confirmed by `lookup_apis`
- Source chunk IDs if used
- Risks, limitations, and confidence

## Device Rules

Normalize device information before selecting target-specific patterns or intrinsics. Do not invent `sm_XX` or `gfxXXX`.

Verify WGMMA, TCGEN05, TMA, `cp.async`, MFMA, LDS, TMEM, `cluster_dims`, `is_cpu=True`, and backend-specific validation behavior against retrieved records and source/API evidence before recommending them.

## Implementation Style

Prefer adapting the closest retrieved pattern over inventing a new structure. Generated TileLang code should follow repository style:

- `import tilelang`
- `import tilelang.language as T`
- `@tilelang.jit` or `@tilelang.jit(out_idx=[...])`
- `@T.prim_func`
- `T.Tensor`
- `with T.Kernel(...)`
- `T.alloc_shared`, `T.alloc_fragment`, `T.alloc_local`, `T.alloc_var`
- `T.copy`, `T.Pipelined`, `T.Parallel`
- TileLang APIs only after `lookup_apis` confirms their symbols, module paths, and visibility

Do not claim validation passed unless a check actually ran and passed.
