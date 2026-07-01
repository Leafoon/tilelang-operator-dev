# TileLang Operator Dev Setup Guide

This guide is a concise operational companion to `README.md`. The supported target is Claude Code.

## Recommended Layout

Use three sibling directories under any local parent directory:

```text
<workspace-root>/
├── tilelang-operator-dev/      # full skill and MCP repository
├── tilelang/                   # official TileLang source repository
└── my-operators/               # independent operator workspace
```

Prepare the repositories:

```bash
mkdir -p <workspace-root>
cd <workspace-root>
git clone https://github.com/Leafoon/tilelang-operator-dev.git
git clone https://github.com/tile-ai/tilelang.git
```

## Mode A: Global Claude Code Configuration

Use this when you want the skill available from any Claude Code workspace.

```bash
cd <workspace-root>/tilelang-operator-dev
bash setup.sh
```

This installs:

```text
~/.claude/skills/tilelang-operator-dev/SKILL.md
~/.claude/.mcp.json
```

Then open an operator workspace:

```bash
mkdir -p <workspace-root>/my-operators
cd <workspace-root>/my-operators
claude .
```

## Mode B: Workspace-Local Configuration

Use this when the operator workspace should carry its own Claude Code MCP config and lightweight skill entrypoint.

```bash
cd <workspace-root>
cp -R tilelang-operator-dev/resources/operator_template my-operators
cd my-operators
claude .
```

The template includes:

```text
.mcp.json
.claude/skills/tilelang-operator-dev/SKILL.md
init_operator.py
example_operator/
```

The workspace `.mcp.json` points to:

```text
${workspaceFolder}/../tilelang-operator-dev/scripts/tilelang_operator_mcp.py
```

## Custom Source Paths

The MCP server auto-detects a sibling or parent `tilelang/` checkout. If your TileLang source lives elsewhere, configure one of:

- `TILELANG_SOURCE_PATH` in `.mcp.json`
- `tilelang_source_path` when calling MCP tools
- an absolute MCP server path if `tilelang-operator-dev` is not a sibling of the workspace

Example `.mcp.json` with explicit source path:

```json
{
  "mcpServers": {
    "tilelang-operator-knowledge": {
      "command": "python3",
      "args": ["<workspace-root>/tilelang-operator-dev/scripts/tilelang_operator_mcp.py"],
      "env": {
        "TILELANG_SOURCE_PATH": "<workspace-root>/tilelang"
      }
    }
  }
}
```

## Create Operators

From the operator workspace:

```bash
python init_operator.py --new-operator fused_moe
python init_operator.py --tilelang-source /absolute/path/to/tilelang --new-operator fused_moe
python init_operator.py --list
```

## Validate The Setup

From `<workspace-root>/tilelang-operator-dev`:

```bash
python scripts/tilelang_operator_mcp.py --check
python -m pytest tests/test_mcp_server.py -q
python .claude/skills/run-tilelang-mcp/driver.py --smoke
python scripts/audit_tilelang_knowledge.py --tilelang-source <workspace-root>/tilelang
```

From Claude Code, ask:

```text
Validate this TileLang operator workspace and show the available capabilities.
```

The expected path is: workspace validation, knowledge validation, capability retrieval, and no code generation until retrieval evidence is available.

## Notes

- Do not copy the full `tilelang-operator-dev` repository into `my-operators/`.
- `my-operators/.claude/skills/tilelang-operator-dev/SKILL.md` is only a lightweight Claude Code entrypoint.
- Workspace-local `tilelang_knowledge/` is optional. The bundled knowledge base is used by default.
