# TileLang Operator Dev

**English** | [中文](README_CN.md)

MCP-backed TileLang operator development skill with workspace validation and device-aware planning.

## Prerequisites

This skill requires a **TileLang workspace** — the AI agent validates the workspace before generating any code. You need one of:

**Option A: Clone the official TileLang repo** (recommended for learning/contributing)

```bash
git clone https://github.com/tile-ai/tilelang.git
cd tilelang
```

**Option B: Your own project with TileLang** (for building custom operators)

```bash
pip install tilelang
mkdir my-project && cd my-project
# Your project must have tilelang/__init__.py accessible (usually via pip install)
# and at least src/transform or src/op, plus examples/ or testing/ or docs/
```

Without a valid TileLang workspace, the skill will stop and refuse to generate code.

## Installation

### Quick Start (Claude Code)

```bash
# 1. Clone the skill
git clone https://github.com/Leafoon/tilelang-operator-dev.git

# 2. Clone TileLang (the workspace the skill validates against)
git clone https://github.com/tile-ai/tilelang.git

# 3. Put the skill into TileLang's .claude/skills/
cp -r tilelang-operator-dev/.claude/skills/run-tilelang-mcp tilelang/.claude/skills/

# 4. Copy MCP config into the TileLang workspace
cp tilelang-operator-dev/resources/.mcp.json tilelang/

# 5. Edit tilelang/.mcp.json — set the script path to the actual location

# 6. Open tilelang/ in Claude Code and ask: "write a GEMM kernel for H100"
```

### Independent Operator Development (Recommended)

Keep your custom operators separate from TileLang source using **dual-workspace mode**:

```bash
# 1. Clone the skill and TileLang
git clone https://github.com/Leafoon/tilelang-operator-dev.git
git clone https://github.com/tile-ai/tilelang.git

# 2. Create your operator workspace (separate from TileLang)
cp -r tilelang-operator-dev/resources/operator_template my-operators
cd my-operators

# 3. Copy .env.example and configure paths
cp .env.example .env
# Edit .env: set TILELANG_SOURCE_PATH=/path/to/tilelang

# 4. Edit .mcp.json — set the script path to the actual location
#    of tilelang-operator-dev/scripts/tilelang_operator_mcp.py

# 5. Open my-operators/ in Claude Code and ask:
#    "develop a fused MoE operator for NVIDIA H100"
```

**Directory structure:**
```
my-projects/
├── tilelang/                          # TileLang source (unchanged)
├── tilelang-operator-dev/             # This skill repo
└── my-operators/                      # Your operators!
    ├── .mcp.json                      # MCP config
    ├── .env                            # TILELANG_SOURCE_PATH=../tilelang
    ├── fused_moe/                      # Your operator 1
    │   ├── operator.py
    │   ├── test_operator.py
    │   └── benchmark.py
    └── flash_attention_v2/             # Your operator 2
        └── ...
```

### Global Install (use from any directory)

Copy the skill to your global Claude Code skills directory:

```bash
git clone https://github.com/Leafoon/tilelang-operator-dev.git
cp -r tilelang-operator-dev/.claude/skills/run-tilelang-mcp ~/.claude/skills/
```

Copy MCP config to your workspace and set `TILELANG_SOURCE_PATH` environment variable.

> **Windows users:** use `.mcp.windows.json` instead — it uses `python` instead of `python3`:
> ```bash
> cp tilelang-operator-dev/resources/.mcp.windows.json your-workspace/.mcp.json
> ```

> **Note:** the knowledge base is built into the MCP server — no need to copy `tilelang_knowledge/` separately. The server automatically uses `resources/tilelang_knowledge/` from the skill package as a fallback.
>
> **Dual-Workspace Mode:** Set `TILELANG_SOURCE_PATH` environment variable to point to your TileLang source checkout. Your operator workspace can be completely separate from TileLang source code.

### Other MCP-compatible Tools

Copy `SKILL.md` to the appropriate skill location and configure MCP using `resources/.mcp.json`:

| Tool | Skill Location | MCP Config |
|------|----------------|------------|
| Claude Code | `.claude/skills/` or `~/.claude/skills/` | `.mcp.json` in project root |
| OpenAI Codex | `.codex-plugin/` | `.mcp.json` in project root |
| Cursor | `.cursorrules` or project root | `.mcp.json` in project root |
| OpenCode | Project config | `.mcp.json` in project root |

## Project Structure

```
tilelang-operator-dev/
├── SKILL.md                         # Core skill instructions
├── metadata.json                    # Skill metadata
├── README.md                        # English
├── README_CN.md                     # Chinese
├── CHANGELOG.md                     # Version history
├── LICENSE                          # Apache-2.0
├── .gitignore
│
├── .claude/                         # Claude Code integration
│   └── skills/
│       └── run-tilelang-mcp/        # MCP server driver skill
│           ├── SKILL.md             # Agent-facing instructions
│           └── driver.py            # Smoke test / tool caller
│
├── scripts/                         # Executable scripts
│   └── tilelang_operator_mcp.py     # MCP server
│
├── resources/                       # Resource files
│   ├── .mcp.json                    # MCP configuration (Linux/Mac)
│   ├── .mcp.windows.json            # MCP configuration (Windows)
│   ├── tilelang_knowledge/          # Pre-generated knowledge base
│   │   ├── retrieval_plan.md
│   │   ├── capability_map.json
│   │   ├── patterns.jsonl
│   │   ├── usage_patterns.jsonl
│   │   ├── apis.jsonl
│   │   ├── source_chunks.jsonl
│   │   ├── semantic_graph.json
│   │   ├── semantic_graph.mmd
│   │   ├── manifest.json
│   │   └── README.md
│   └── assets/
│       └── app-icon.png
│
├── examples/                        # Usage examples
│   ├── basic-gemm.md
│   ├── device-adaptation.md
│   └── failure-cases.md
│
└── tests/                           # Test cases
    ├── test_mcp_server.py           # Automated pytest suite
    ├── test_cases.md
    └── eval.yaml
```

## What Each File Does

| File | Purpose | Who Reads It |
|------|---------|--------------|
| `SKILL.md` | AI agent instructions (when/how to use tools) | AI agent (Claude, GPT, etc.) |
| `metadata.json` | Skill metadata (version, author, etc.) | AI tools, package managers |
| `.claude/skills/run-tilelang-mcp/SKILL.md` | MCP driver skill instructions | Claude Code (auto-loaded) |
| `.claude/skills/run-tilelang-mcp/driver.py` | MCP server smoke test and tool caller | Developers, CI/CD |
| `scripts/tilelang_operator_mcp.py` | MCP server implementation | AI tool runtime |
| `resources/.mcp.json` | MCP server connection config | AI tools (Claude Code, Codex, etc.) |
| `resources/tilelang_knowledge/` | Pre-generated knowledge base | MCP server |
| `examples/` | Usage examples | Developers |
| `tests/` | Test cases and eval config | CI/CD, developers |

## MCP Tools

The MCP server provides these tools (13 total):

### Core Validation & Search
- `inspect_tilelang_workspace`: validate TileLang repository and delivery directory presence
- `validate_knowledge_base`: parse and count required JSON/JSONL delivery files
- `normalize_device_profile`: normalize vendor/model/target without inventing unknown architectures
- `search_capabilities`: search `capability_map.json`
- `search_patterns`: search `patterns.jsonl`
- `search_usage_patterns`: search `usage_patterns.jsonl`
- `lookup_apis`: search `apis.jsonl`
- `get_source_chunks`: retrieve focused fallback chunks from `source_chunks.jsonl`
- `trace_semantic_graph`: inspect related graph nodes and edges
- `build_operator_retrieval_plan`: assemble a structured operator retrieval plan

### New Quality & Guidance Tools
- `search_troubleshooting`: search troubleshooting knowledge base for common issues, errors, and solutions
- `validate_operator_code`: static analysis of TileLang operator code for syntax, structure, and common issues
- `operator_development_wizard`: step-by-step guided workflow for TileLang operator development from intent to validation

## Standard Workflow

1. Validate workspace with `inspect_tilelang_workspace`
2. Validate delivery files with `validate_knowledge_base`
3. Normalize target device with `normalize_device_profile`
4. Search capability, pattern, usage, API, and source chunk layers
5. Trace semantic graph only when dependencies or relationships are needed
6. Generate the operator plan, code, explanation, and validation plan using retrieved evidence
7. Stop instead of guessing when evidence is missing or inconsistent

## Failure Policy

The skill must stop when:

- The current workspace is not a TileLang repository
- `tilelang_knowledge/` is missing
- Critical delivery files are missing
- JSON/JSONL parsing fails
- Selected evidence paths do not exist in the current repository

## Device Strategy

Device recommendations use delivery fields:

- `device_adaptation`
- `device_strategy`
- `device_execution_notes`
- `device_notes`

Conservative with WGMMA, TCGEN05, TMA, `cp.async`, MFMA, LDS, TMEM, `cluster_dims`, and `is_cpu=True`.

## Development

> **Note:** all commands below use `python`. On some Linux systems you may need `python3` instead.

### Running the MCP Server

```bash
python scripts/tilelang_operator_mcp.py --check
```

### Smoke Test (all 10 tools)

```bash
python .claude/skills/run-tilelang-mcp/driver.py --smoke
```

### List Available Tools

```bash
python .claude/skills/run-tilelang-mcp/driver.py --list
```

### Call a Single Tool

```bash
python .claude/skills/run-tilelang-mcp/driver.py --call normalize_device_profile --args '{"vendor":"nvidia","model":"H100","target":"cuda"}'
```

### Raw JSON-RPC Test

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python scripts/tilelang_operator_mcp.py
```

### Running Tests

```bash
python -m pytest tests/test_mcp_server.py -v
```

See `tests/test_cases.md` for additional manual test cases.

## License

Apache-2.0
