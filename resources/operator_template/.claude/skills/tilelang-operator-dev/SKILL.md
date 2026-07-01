---
name: tilelang-operator-dev
description: Use when developing, adapting, explaining, or validating TileLang operators in Claude Code from an independent operator workspace. Loads tilelang-operator-knowledge through the workspace .mcp.json and uses sibling TileLang source plus bundled or workspace-local knowledge.
---

# TileLang Operator Dev

Use this workspace-local skill for custom TileLang operator work. This directory is only a light Claude Code entrypoint; it is not a copy of the full `tilelang-operator-dev` repository.

Expected sibling layout:

```text
<parent>/
├── tilelang-operator-dev/
├── tilelang/
└── my-operators/
```

The workspace `.mcp.json` points to `../tilelang-operator-dev/scripts/tilelang_operator_mcp.py`. The MCP server auto-detects the sibling `tilelang/` repository and uses bundled `resources/tilelang_knowledge/` unless this workspace provides a complete local `tilelang_knowledge/` including troubleshooting records.

## Required Workflow

1. Call `inspect_tilelang_workspace`.
2. Call `validate_knowledge_base`.
3. Normalize any provided device with `normalize_device_profile`.
4. Retrieve capabilities, patterns, usage records, APIs, and source chunks before writing code.
5. Generate code only after a retrieval trace is available.
6. Validate generated code with `validate_operator_code`.
7. Use `search_troubleshooting` when compile/runtime/performance errors occur.

For guided work, call `operator_development_wizard`.

## Hard Stops

Do not generate code if TileLang source cannot be resolved, no valid knowledge base is available, JSON/JSONL parsing fails, or the selected operator requires missing evidence paths.

## Device Rules

Be conservative with target-specific features. Verify WGMMA, TCGEN05, TMA, `cp.async`, MFMA, LDS, TMEM, `cluster_dims`, and `is_cpu=True` against delivery records and source/API evidence before recommending them.
