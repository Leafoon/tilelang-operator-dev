# TileLang Operator Workspace

This is an independent Claude Code workspace for custom TileLang operators. It is intended to live next to:

```text
<parent>/
├── tilelang-operator-dev/      # full skill and MCP repository
├── tilelang/                   # official TileLang source repository
└── my-operators/               # this workspace
```

This workspace does not contain a full copy of `tilelang-operator-dev`. The local `.claude/skills/tilelang-operator-dev/SKILL.md` file is only a lightweight Claude Code entrypoint.

## What Is Included

- `.mcp.json`: loads `tilelang-operator-knowledge` from `../tilelang-operator-dev/scripts/tilelang_operator_mcp.py`
- `.claude/skills/tilelang-operator-dev/SKILL.md`: workspace-local Claude Code skill entrypoint
- `init_operator.py`: creates new operator directories from the example template
- `example_operator/`: starter layout for implementation, tests, benchmarks, and notes

## Start Claude Code

```bash
cd my-operators
claude .
```

The MCP server resolves TileLang source in this order:

1. Explicit `tilelang_source_path` tool argument
2. `TILELANG_SOURCE_PATH` environment variable
3. Sibling or parent `tilelang/` directory
4. Current workspace as a backward-compatible fallback

The knowledge base resolves from workspace-local `tilelang_knowledge/` first, then bundled `../tilelang-operator-dev/resources/tilelang_knowledge/`. This template does not create a local `tilelang_knowledge/` directory; add one only when you intentionally need a complete local override.

## Create Operators

Create a new operator from the template:

```bash
python init_operator.py --new-operator fused_moe
```

List existing operators:

```bash
python init_operator.py --list
```

Each generated operator directory contains:

- `operator.py`: TileLang implementation
- `test_operator.py`: correctness tests
- `benchmark.py`: performance checks
- `README.md`: operator-specific notes

## Expected Claude Code Workflow

Ask Claude Code from this workspace. The skill should:

1. Validate the workspace with `inspect_tilelang_workspace`.
2. Validate the knowledge base with `validate_knowledge_base`.
3. Normalize hardware details with `normalize_device_profile`.
4. Search capabilities, patterns, usage records, APIs, and source chunks.
5. Build a retrieval plan before generating code.
6. Validate generated code with `validate_operator_code`.
7. Use `search_troubleshooting` for errors.

Example prompts:

- "Develop a grouped GEMM TileLang operator for NVIDIA H100."
- "Validate this operator and explain why it may fail on A100."
- "Adapt this kernel for AMD MI300X and show the risks."

## Troubleshooting

If TileLang source is not found, place the official repository at `../tilelang` or set `TILELANG_SOURCE_PATH` in `.mcp.json`.

If the MCP server is not found, check that this workspace is next to `tilelang-operator-dev` or update `.mcp.json` to use an absolute path.

If knowledge validation fails, ensure `../tilelang-operator-dev/resources/tilelang_knowledge/` exists. Only create workspace-local `tilelang_knowledge/` for custom overrides, and copy the complete delivery set before editing it.
