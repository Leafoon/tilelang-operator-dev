# TileLang Operator Dev

[English](README.md) | [简体中文](README.zh-CN.md)

TileLang Operator Dev is a Claude Code skill and MCP server for building TileLang operators from an independent development workspace. It validates the workspace, retrieves TileLang-specific knowledge, normalizes device targets, and guides implementation, validation, and troubleshooting before code is generated.

## What It Provides

- **Claude Code skill**: `tilelang-operator-dev` for TileLang operator design, implementation, adaptation, validation, and explanation.
- **MCP server**: `tilelang-operator-knowledge` with 13 tools for workspace validation, knowledge retrieval, planning, troubleshooting, and static code checks.
- **Independent operator workspaces**: keep custom operators outside the TileLang source tree.
- **Bundled knowledge base**: use `resources/tilelang_knowledge/` by default, with optional workspace-local overrides.
- **Device-aware planning**: normalize NVIDIA, AMD, CPU, Apple Silicon, and WebGPU targets before selecting target-specific patterns; recognize other accelerator vendors as constrained until backend evidence is available.

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

- Python 3.10+
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

## Quick Start

The shortest recommended path is the global configuration mode. It keeps the full skill and MCP server in one checkout, while your operators live in a separate workspace.

```bash
mkdir -p <workspace-root>
cd <workspace-root>

git clone https://github.com/Leafoon/tilelang-operator-dev.git
git clone https://github.com/tile-ai/tilelang.git
mkdir -p my-operators

cd tilelang-operator-dev
bash setup.sh

cd ../my-operators
claude .
```

If your default `python3` is older than 3.10, run setup with an explicit interpreter:

```bash
cd <workspace-root>/tilelang-operator-dev
PYTHON=/path/to/python3.10 bash setup.sh
```

Inside Claude Code, start with a direct request such as:

```text
Use the tilelang-operator-dev skill. Inspect this workspace, confirm TileLang source and knowledge availability, then create a retrieval plan for an fp16 GEMM operator on NVIDIA H100.
```

## Configuration Modes

### Option A: Global Claude Code Configuration

Use this mode when you want Claude Code to discover the skill and MCP server from any operator workspace.

```bash
cd <workspace-root>/tilelang-operator-dev
bash setup.sh
```

Use `PYTHON=/path/to/python3.10 bash setup.sh` if Claude Code should launch the MCP server with a specific Python interpreter.

This installs or updates:

- Skill: `~/.claude/skills/tilelang-operator-dev/SKILL.md`
- User-scoped MCP config: `~/.claude.json`
- MCP server target: `<workspace-root>/tilelang-operator-dev/scripts/tilelang_operator_mcp.py`

If `~/.claude.json` already exists, `setup.sh` preserves existing user-scoped MCP servers and upserts only `tilelang-operator-knowledge`. It also creates a timestamped backup before writing.

The generated MCP config has this shape:

```json
{
  "mcpServers": {
    "tilelang-operator-knowledge": {
      "type": "stdio",
      "command": "python3",
      "args": ["<workspace-root>/tilelang-operator-dev/scripts/tilelang_operator_mcp.py"],
      "env": {}
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

You can check whether Claude Code sees the user-scoped server with:

```bash
claude mcp list
```

### Option B: Workspace-Local Configuration

Use this mode when the operator workspace should carry its own `.mcp.json` and lightweight skill entrypoint.

```bash
cd <workspace-root>
cp -R tilelang-operator-dev/resources/operator_template my-operators
cd my-operators
claude .
```

Create a new operator directory from the template:

```bash
python init_operator.py --new-operator fused_moe_gemm
```

The template includes:

- `.mcp.json`, pointing to `../tilelang-operator-dev/scripts/tilelang_operator_mcp.py`
- `.claude/skills/tilelang-operator-dev/SKILL.md`, a lightweight Claude Code skill entrypoint
- `init_operator.py`, for creating operator directories and validating a nearby, explicit, or `TILELANG_SOURCE_PATH` TileLang checkout
- `example_operator/`, a starter operator layout

The template does not include `tilelang_knowledge/`. Claude Code normally uses the bundled knowledge base from `tilelang-operator-dev`; create a workspace-local `tilelang_knowledge/` only for a complete custom override.

Default workspace MCP config:

```json
{
  "mcpServers": {
    "tilelang-operator-knowledge": {
      "command": "python3",
      "args": [
        "${CLAUDE_PROJECT_DIR:-.}/../tilelang-operator-dev/scripts/tilelang_operator_mcp.py"
      ]
    }
  }
}
```

This relative path assumes `my-operators` and `tilelang-operator-dev` are siblings. If your directories are arranged differently, replace it with an absolute path.

Project-scoped `.mcp.json` servers may require approval the first time you open the workspace. Use `/mcp` inside Claude Code or `claude mcp list` from the shell to inspect the connection state.

To point the workspace at a non-sibling TileLang checkout, add `TILELANG_SOURCE_PATH` to the MCP server environment or pass `tilelang_source_path` in tool arguments when debugging MCP calls. For normal Claude Code use, the sibling `tilelang/` checkout or the environment variable is the least ambiguous setup.

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

## Using It In Claude Code

Start Claude Code from the operator workspace, not from `tilelang-operator-dev`:

```bash
cd <workspace-root>/my-operators
claude .
```

In Claude Code, you do not normally call MCP tools by hand. Ask for the operator task in natural language and mention `tilelang-operator-dev` when you want to force the skill to trigger. The skill should validate and retrieve before writing code:

1. Validate workspace: `inspect_tilelang_workspace`
2. Validate knowledge base: `validate_knowledge_base`
3. Normalize device: `normalize_device_profile`
4. Search capabilities, patterns, usage records, APIs, and source chunks
5. Build a retrieval plan
6. Generate code or explanation
7. Validate generated code
8. Troubleshoot compile, runtime, or performance issues if needed

The first answer should include a retrieval trace before implementation: operator workspace, TileLang source path, knowledge path, device profile, selected capability/pattern/usage records, API symbols, source fallback chunks, risks, and confidence.

### Recommended Prompt Structure

Use this structure for implementation requests:

```text
Use the tilelang-operator-dev skill.

Task:
- Build / adapt / explain / validate a TileLang operator.

Operator:
- Type: GEMM / grouped GEMM / attention / reduction / custom
- Shapes: M=?, N=?, K=?, batch=?, heads=?, block sizes if known
- Dtypes: input=?, accumulator=?, output=?
- Layout: row-major / column-major / transposed / packed / sparse

Hardware:
- Vendor and model: NVIDIA H100 / A100 / AMD MI300X / CPU / ...
- Target if known: cuda -arch=sm_90 / hip -mcpu=gfx942 / llvm / ...
- Required features: WGMMA / TMA / cp.async / MFMA / none / unknown

Constraints:
- Correctness tolerance:
- Performance goal:
- Memory limit:
- Must reuse or avoid:

Existing material:
- Paste current code, error logs, benchmark output, or say "from scratch".

Expected output:
- Retrieval trace first, then implementation plan, code, tests, and validation steps.
```

For troubleshooting, use this structure:

```text
Use the tilelang-operator-dev skill to debug this TileLang issue.

Environment:
- TileLang source path:
- Python version:
- GPU/CPU model and target:

Command I ran:
<paste command>

Error:
<paste full error log>

Code:
<paste relevant operator code>

Expected:
<what should have happened>
```

### Example Prompts

- "Develop a basic fp16 GEMM operator for NVIDIA H100 in TileLang."
- "Adapt this H100 TileLang kernel for A100 and explain the required scheduling changes."
- "Validate this TileLang operator and identify likely correctness or performance issues."
- "Walk me through a grouped GEMM operator for MoE-style workloads."
- "Use tilelang-operator-dev to inspect this workspace and tell me whether the MCP knowledge base is available."
- "Use tilelang-operator-dev to debug this dtype mismatch. Here is the full error log: ..."
- "I want to target Huawei Ascend 910B. Check whether the local TileLang checkout provides backend evidence before proposing any CANN-specific code."

### What Claude Code Should Do

For code generation, a good response should:

- show the retrieval trace before code;
- explain which TileLang pattern and API records were selected;
- state device confidence and unresolved hardware questions;
- generate code only after the relevant API symbols are confirmed;
- provide correctness tests and benchmark commands;
- clearly separate verified behavior from assumptions.

For unsupported or constrained hardware, such as Huawei Ascend without `tilelang-ascend` evidence, MetaX/Muxi, Moore Threads, Cambricon, Biren, Iluvatar, or Kunlun, a good response should not invent vendor targets. It should ask for backend/compiler evidence or fall back to architecture-neutral design guidance.

## MCP Tools

| Tool | Purpose |
|------|---------|
| `inspect_tilelang_workspace` | Validate operator workspace, TileLang source, and knowledge availability |
| `validate_knowledge_base` | Validate delivery files, parse JSON/JSONL records, and audit evidence paths against the resolved TileLang source when available |
| `normalize_device_profile` | Normalize vendor/model/target information |
| `search_capabilities` | Find matching operator capability categories |
| `search_patterns` | Retrieve reusable implementation patterns; `capability_id` filters through `capability_map.related_patterns` |
| `search_usage_patterns` | Retrieve compile, run, compare, and profile workflows |
| `lookup_apis` | Confirm TileLang API signatures, modules, and visibility |
| `get_source_chunks` | Retrieve focused source fallback chunks from the knowledge delivery |
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
| Huawei Ascend | No target is inferred from the main TileLang checkout. Preserve user-supplied targets only when backed by the external `tilelang-ascend` checkout or equivalent backend/compiler evidence. | Constrained until external backend evidence is provided |
| Other accelerator vendors: MetaX/Muxi, Moore Threads, Cambricon, Biren, Iluvatar, Kunlun | No target is inferred. Preserve only user-supplied targets when backed by source and compiler evidence. | Constrained |

Architecture-specific features such as WGMMA, TCGEN05, TMA, `cp.async`, MFMA, LDS, TMEM, `cluster_dims`, and `is_cpu=True` must be verified against retrieved knowledge and source/API evidence before they are recommended.

For Huawei Ascend, MetaX/Muxi, Moore Threads, Cambricon, Biren, Iluvatar, Kunlun, or other accelerator vendors, the skill can identify the vendor family but must not invent CANN, MUSA, MACA, MLU, XPU, or other vendor targets without local TileLang backend, compiler, runtime, and example evidence. The main TileLang README references Ascend support through `tilelang-ascend`; use that repository as source evidence when working on Ascend-specific operators.

## Validation

From the `tilelang-operator-dev` repository:

```bash
python -m pytest tests/test_mcp_server.py -q
python scripts/tilelang_operator_mcp.py --check
python .claude/skills/run-tilelang-mcp/driver.py --smoke
python scripts/audit_tilelang_knowledge.py --tilelang-source <workspace-root>/tilelang
```

The `run-tilelang-mcp` skill and driver are retained for MCP server development and smoke testing. They are not the default user-facing operator development skill.

The knowledge audit checks JSON/JSONL parsing, source evidence paths, line ranges, and official `examples/` directory coverage against the TileLang checkout you provide.

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
