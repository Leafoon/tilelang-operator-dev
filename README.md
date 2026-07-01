# TileLang Operator Dev

[English](README.md) | [简体中文](README.zh-CN.md)

TileLang Operator Dev is a Claude Code skill and MCP server for building TileLang operators from an independent development workspace. It validates the workspace, retrieves TileLang-specific knowledge, normalizes device targets, and guides implementation, validation, and troubleshooting before code is generated.

## What It Provides

- **Claude Code skill**: `tilelang-operator-dev` for TileLang operator design, implementation, adaptation, validation, and explanation.
- **MCP server**: `tilelang-operator-knowledge` with 13 tools for workspace validation, knowledge retrieval, planning, troubleshooting, and static code checks.
- **Independent operator workspaces**: keep custom operators outside the TileLang source tree.
- **Bundled knowledge base**: use `resources/tilelang_knowledge/` by default, with optional workspace-local overrides.
- **Device-aware planning**: normalize NVIDIA, AMD, CPU, Apple Silicon, and WebGPU targets before selecting target-specific patterns.

## Recommended Directory Layout

The recommended layout keeps three directories as siblings under any local parent directory. The parent can be anywhere on the user's machine, for example a project folder, a scratch directory, or a shared workspace.

```text
<workspace-root>/
├── tilelang-operator-dev/      # this repository: skill, MCP server, bundled knowledge
├── tilelang/                   # official TileLang source repository
└── my-operators/               # independent Claude Code operator workspace
```

Open Claude Code from the operator workspace:

```bash
cd <workspace-root>/my-operators
claude .
```

`my-operators` should not contain a full nested copy of `tilelang-operator-dev`. If workspace-local skill discovery is used, `my-operators/.claude/skills/tilelang-operator-dev/SKILL.md` is only a lightweight Claude Code entrypoint.

## Prerequisites

- Python 3.8+
- Claude Code
- A local checkout of the official TileLang repository

Example setup:

```bash
mkdir -p <workspace-root>
cd <workspace-root>
git clone https://github.com/Leafoon/tilelang-operator-dev.git
git clone https://github.com/tile-ai/tilelang.git
```

Replace `<workspace-root>` with any directory you control.

## Configuration Modes

### Option A: Global Claude Code Configuration

Use this mode when you want Claude Code to discover the skill and MCP server from any operator workspace.

```bash
cd <workspace-root>/tilelang-operator-dev
bash setup.sh
```

This installs:

- Skill: `~/.claude/skills/tilelang-operator-dev/SKILL.md`
- MCP config: `~/.claude/.mcp.json`
- MCP server target: `<workspace-root>/tilelang-operator-dev/scripts/tilelang_operator_mcp.py`

The generated MCP config has this shape:

```json
{
  "mcpServers": {
    "tilelang-operator-knowledge": {
      "command": "python3",
      "args": ["<workspace-root>/tilelang-operator-dev/scripts/tilelang_operator_mcp.py"]
    }
  }
}
```

After setup, restart Claude Code and open an operator workspace:

```bash
mkdir -p <workspace-root>/my-operators
cd <workspace-root>/my-operators
claude .
```

### Option B: Workspace-Local Configuration

Use this mode when the operator workspace should carry its own `.mcp.json` and lightweight skill entrypoint.

```bash
cd <workspace-root>
cp -R tilelang-operator-dev/resources/operator_template my-operators
cd my-operators
claude .
```

The template includes:

- `.mcp.json`, pointing to `../tilelang-operator-dev/scripts/tilelang_operator_mcp.py`
- `.claude/skills/tilelang-operator-dev/SKILL.md`, a lightweight Claude Code skill entrypoint
- `init_operator.py`, for creating operator directories
- `example_operator/`, a starter operator layout

Default workspace MCP config:

```json
{
  "mcpServers": {
    "tilelang-operator-knowledge": {
      "command": "python3",
      "args": [
        "${workspaceFolder}/../tilelang-operator-dev/scripts/tilelang_operator_mcp.py"
      ]
    }
  }
}
```

This relative path assumes `my-operators` and `tilelang-operator-dev` are siblings. If your directories are arranged differently, replace it with an absolute path.

## Source And Knowledge Resolution

The MCP server resolves the TileLang source repository in this order:

1. Explicit `tilelang_source_path` tool argument
2. `TILELANG_SOURCE_PATH` environment variable
3. Auto-detected sibling or parent `tilelang/` directory
4. Active workspace as a backward-compatible fallback

The knowledge base resolves in this order:

1. Workspace-local `tilelang_knowledge/`, if present and complete enough
2. Bundled `resources/tilelang_knowledge/` from this repository

This keeps the operator workspace small and focused on custom operators.

## Standard Claude Code Workflow

Ask Claude Code for TileLang operator work from the operator workspace. The skill should validate and retrieve before writing code:

1. Validate workspace: `inspect_tilelang_workspace`
2. Validate knowledge base: `validate_knowledge_base`
3. Normalize device: `normalize_device_profile`
4. Search capabilities, patterns, usage records, APIs, and source chunks
5. Build a retrieval plan
6. Generate code or explanation
7. Validate generated code
8. Troubleshoot compile, runtime, or performance issues if needed

Example prompts:

- "Develop a basic fp16 GEMM operator for NVIDIA H100 in TileLang."
- "Adapt this H100 TileLang kernel for A100 and explain the required scheduling changes."
- "Validate this TileLang operator and identify likely correctness or performance issues."
- "Walk me through a grouped GEMM operator for MoE-style workloads."

## MCP Tools

| Tool | Purpose |
|------|---------|
| `inspect_tilelang_workspace` | Validate operator workspace, TileLang source, and knowledge availability |
| `validate_knowledge_base` | Validate required delivery files and parse JSON/JSONL records |
| `normalize_device_profile` | Normalize vendor/model/target information |
| `search_capabilities` | Find matching operator capability categories |
| `search_patterns` | Retrieve reusable implementation patterns |
| `search_usage_patterns` | Retrieve compile, run, compare, and profile workflows |
| `lookup_apis` | Confirm TileLang API signatures, modules, and visibility |
| `get_source_chunks` | Retrieve focused source fallback chunks |
| `trace_semantic_graph` | Trace concepts, symbols, and pattern dependencies |
| `build_operator_retrieval_plan` | Assemble a structured operator retrieval plan |
| `search_troubleshooting` | Search known error patterns and fixes |
| `validate_operator_code` | Run static checks on generated TileLang code |
| `operator_development_wizard` | Guide a step-by-step operator development workflow |

## Device Support

| Device family | Typical target | Confidence |
|---------------|----------------|------------|
| NVIDIA A100 / Ampere | `cuda -arch=sm_80` | High when confirmed by user or source evidence |
| NVIDIA H100 / Hopper | `cuda -arch=sm_90` | High when confirmed by user or source evidence |
| NVIDIA B100 / Blackwell | `cuda -arch=sm_100a` | Medium until current repo support is verified |
| AMD MI300X / MI350 | `hip -mcpu=gfx940` / `gfx950` | Medium when exact gfx arch is known |
| CPU | `llvm` or `c` | High for supported CPU paths |
| Apple Silicon | `metal` | Medium, verify repository support |
| WebGPU | `webgpu` | Low to medium, verify repository support |

Architecture-specific features such as WGMMA, TCGEN05, TMA, `cp.async`, MFMA, LDS, TMEM, `cluster_dims`, and `is_cpu=True` must be verified against retrieved knowledge and source/API evidence before they are recommended.

## Validation

From the `tilelang-operator-dev` repository:

```bash
python -m pytest tests/test_mcp_server.py -q
python scripts/tilelang_operator_mcp.py --check
python .claude/skills/run-tilelang-mcp/driver.py --smoke
```

The `run-tilelang-mcp` skill and driver are retained for MCP server development and smoke testing. They are not the default user-facing operator development skill.

## Troubleshooting

### Claude Code does not trigger the operator skill

Confirm the installed or workspace-local skill path:

```text
~/.claude/skills/tilelang-operator-dev/SKILL.md
```

or:

```text
<workspace-root>/my-operators/.claude/skills/tilelang-operator-dev/SKILL.md
```

### MCP server is not available

Check `.mcp.json` and verify that the script path points to the cloned `tilelang-operator-dev` repository:

```text
<workspace-root>/tilelang-operator-dev/scripts/tilelang_operator_mcp.py
```

Then run:

```bash
python <workspace-root>/tilelang-operator-dev/scripts/tilelang_operator_mcp.py --check
```

### TileLang source is not found

Use one of these fixes:

- Place the official repository at `<workspace-root>/tilelang`.
- Set `TILELANG_SOURCE_PATH` in the MCP config.
- Pass `tilelang_source_path` when calling MCP tools.

### Knowledge base validation fails

The bundled knowledge base should be present at:

```text
<workspace-root>/tilelang-operator-dev/resources/tilelang_knowledge/
```

Only add workspace-local `tilelang_knowledge/` if you need custom overrides.

## License

Apache-2.0
