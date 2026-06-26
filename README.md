# TileLang Operator Dev

**English** | [中文](README_CN.md)

MCP-backed TileLang operator development skill with workspace validation, device-aware planning, and smart auto-detection.

## Features

- 🔍 **Smart Auto-Detection** - Automatically finds TileLang source repository (zero configuration)
- 🔄 **Dual-Workspace Mode** - Develop operators separately from TileLang source
- 📚 **Built-in Knowledge Base** - 13 MCP tools with pre-generated patterns, APIs, and examples
- 🎯 **Device-Aware Planning** - Support for NVIDIA, AMD, CPU, Apple Silicon, and WebGPU
- ✅ **Validation First** - Mandatory workspace validation before code generation
- 🛠️ **Development Wizard** - Step-by-step guided workflow for operator development

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

# 2. Create your operator workspace (copy the template)
cp -r tilelang-operator-dev/resources/operator_template my-operators
cd my-operators

# 3. Open in Claude Code — auto-detection finds TileLang automatically!
claude .
```

**No configuration needed!** The MCP server automatically detects TileLang source by searching:
1. Sibling `tilelang/` directory (most common)
2. Up to 3 parent levels

**Directory structure:**
```
my-projects/
├── tilelang/                          # TileLang source (unchanged)
├── tilelang-operator-dev/             # This skill repo
└── my-operators/                      # Your operators!
    ├── .mcp.json                      # MCP config
    ├── init_operator.py               # Operator creation utility
    ├── fused_moe/                     # Your operator 1
    │   ├── operator.py
    │   ├── test_operator.py
    │   └── benchmark.py
    └── flash_attention_v2/            # Your operator 2
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
├── SETUP_GUIDE.md                   # Detailed setup guide
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
│   └── tilelang_operator_mcp.py     # MCP server (13 tools)
│
├── resources/                       # Resource files
│   ├── .mcp.json                    # MCP configuration (Linux/Mac)
│   ├── .mcp.windows.json            # MCP configuration (Windows)
│   ├── tilelang_knowledge/          # Pre-generated knowledge base
│   │   ├── retrieval_plan.md        # Step-by-step retrieval procedure
│   │   ├── capability_map.json      # Capability routing map
│   │   ├── patterns.jsonl           # Reusable operator patterns
│   │   ├── usage_patterns.jsonl     # Call sequences and workflows
│   │   ├── apis.jsonl               # API signatures and visibility
│   │   ├── source_chunks.jsonl      # Source code fallback chunks
│   │   ├── semantic_graph.json      # Concept/symbol/pattern graph
│   │   ├── semantic_graph.mmd       # Mermaid graph for humans
│   │   ├── manifest.json            # Repository metadata
│   │   ├── troubleshooting.jsonl    # Common issues and solutions
│   │   └── README.md                # Knowledge base documentation
│   ├── operator_template/           # Template for independent operators
│   │   ├── .mcp.json                # Pre-configured MCP config
│   │   ├── .gitignore               # Git ignore rules
│   │   ├── README.md                # Template documentation
│   │   ├── init_operator.py         # Workspace initialization script
│   │   └── example_operator/        # Example operator
│   │       ├── operator.py          # Operator implementation template
│   │       ├── test_operator.py     # Test template
│   │       ├── benchmark.py         # Benchmark template
│   │       └── README.md            # Operator documentation template
│   └── assets/
│       └── app-icon.png
│
├── examples/                        # Usage examples
│   ├── basic-gemm.md               # Basic GEMM workflow
│   ├── device-adaptation.md        # Device-specific adaptation
│   └── failure-cases.md            # Error handling examples
│
└── tests/                           # Test cases
    ├── test_mcp_server.py           # Automated pytest suite (40+ tests)
    ├── test_cases.md                # Manual test cases
    └── eval.yaml                    # Evaluation configuration
```

## MCP Tools

The MCP server provides **13 tools** for TileLang operator development:

### Core Validation & Search

| Tool | Description |
|------|-------------|
| `inspect_tilelang_workspace` | Validate TileLang repository and knowledge base presence. Supports dual-workspace mode. |
| `validate_knowledge_base` | Parse and count required JSON/JSONL delivery files. |
| `normalize_device_profile` | Normalize vendor/model/target without inventing unknown architectures. |
| `search_capabilities` | Search `capability_map.json` for operator capabilities. |
| `search_patterns` | Search `patterns.jsonl` for operator implementation patterns. |
| `search_usage_patterns` | Search `usage_patterns.jsonl` for example workflows. |
| `lookup_apis` | Search `apis.jsonl` for TileLang API symbols and signatures. |
| `get_source_chunks` | Retrieve focused fallback chunks from `source_chunks.jsonl`. |
| `trace_semantic_graph` | Inspect related graph nodes and edges. |
| `build_operator_retrieval_plan` | Assemble a structured operator retrieval plan. |

### Quality & Guidance Tools

| Tool | Description |
|------|-------------|
| `search_troubleshooting` | Search troubleshooting knowledge base for common issues, errors, and solutions. |
| `validate_operator_code` | Static analysis of TileLang operator code for syntax, structure, and common issues. |
| `operator_development_wizard` | Step-by-step guided workflow for TileLang operator development (12 stages). |

## Standard Workflow

1. **Workspace Validation** - `inspect_tilelang_workspace`
2. **Knowledge Validation** - `validate_knowledge_base`
3. **Device Normalization** - `normalize_device_profile`
4. **Capability Search** - `search_capabilities`
5. **Pattern Search** - `search_patterns`
6. **Usage Pattern Search** - `search_usage_patterns`
7. **API Confirmation** - `lookup_apis`
8. **Source Fallback** - `get_source_chunks`
9. **Dependency Tracing** - `trace_semantic_graph`
10. **Retrieval Plan** - `build_operator_retrieval_plan`
11. **Implementation** - Generate code, explanation, or validation plan
12. **Code Validation** - `validate_operator_code`
13. **Troubleshooting** - `search_troubleshooting` (if errors occur)

Only step 11 may generate final operator code.

## Failure Policy

The skill must stop immediately when:

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

**Conservative with architecture-specific features:**
- WGMMA (NVIDIA only, verify support)
- TCGEN05 (Hopper+ only)
- TMA (Hopper+ only)
- `cp.async` (Ampere+ only)
- MFMA (AMD only)
- LDS (AMD shared memory)
- TMEM (verify support)
- `cluster_dims` (Hopper+ only)
- `is_cpu=True` (CPU backend only)

## Development

> **Note:** all commands below use `python`. On some Linux systems you may need `python3` instead.

### Running the MCP Server

```bash
python scripts/tilelang_operator_mcp.py --check
```

### Smoke Test (all 13 tools)

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

## Documentation

| Document | Description |
|----------|-------------|
| [README.md](README.md) | This file - English documentation |
| [README_CN.md](README_CN.md) | Chinese documentation |
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | Detailed setup guide for dual-workspace mode |
| [CHANGELOG.md](CHANGELOG.md) | Version history and release notes |
| [SKILL.md](SKILL.md) | Core skill instructions for AI agents |
| [examples/](examples/) | Usage examples and workflows |
| [tests/](tests/) | Test cases and evaluation configuration |

## License

Apache-2.0
