# TileLang Operator Dev Setup Guide

This file is intentionally short. The complete and authoritative setup, usage,
Claude Code prompt structure, device-support policy, and troubleshooting guide
live in `README.md` and `README.zh-CN.md`.

## Recommended Layout

Use three sibling directories under any local parent directory:

```text
<workspace-root>/
├── tilelang-operator-dev/
├── tilelang/
└── my-operators/
```

## Global Claude Code Setup

```bash
cd <workspace-root>/tilelang-operator-dev
bash setup.sh

cd ../my-operators
claude .
```

Use an explicit Python interpreter when needed:

```bash
PYTHON=/path/to/python3.10 bash setup.sh
```

`setup.sh` installs the skill to `~/.claude/skills/tilelang-operator-dev/SKILL.md`
and upserts the user-scoped MCP server in `~/.claude.json`.

## Workspace-Local Setup

```bash
cd <workspace-root>
cp -R tilelang-operator-dev/resources/operator_template my-operators
cd my-operators
claude .
```

Create an operator from the template:

```bash
python init_operator.py --new-operator fused_moe
```

## Validate The Setup

From `<workspace-root>/tilelang-operator-dev`:

```bash
python scripts/tilelang_operator_mcp.py --check
python -m pytest tests/test_mcp_server.py -q
python .claude/skills/run-tilelang-mcp/driver.py --smoke
python scripts/audit_tilelang_knowledge.py --tilelang-source <workspace-root>/tilelang
```

## Claude Code Prompt

Start from the operator workspace and ask Claude Code:

```text
Use the tilelang-operator-dev skill. Inspect this workspace, validate TileLang
source and knowledge availability, then build a retrieval plan before writing
code.
```

For detailed prompt templates and constrained hardware policy, see `README.md`.
