# TileLang Operator Development Setup Guide

This guide explains how to set up an independent operator development workspace separate from the TileLang source repository.

## Table of Contents

- [Overview](#overview)
- [Directory Structure](#directory-structure)
- [Step-by-Step Setup](#step-by-step-setup)
- [Environment Configuration](#environment-configuration)
- [MCP Configuration](#mcp-configuration)
- [Creating New Operators](#creating-new-operators)
- [Troubleshooting](#troubleshooting)

## Overview

The tilelang-operator-dev skill supports **two modes of operation**:

### 1. Single-Workspace Mode (Legacy)
- Your operator code lives inside the TileLang source repository
- No additional configuration needed
- Good for: Contributing to TileLang itself

### 2. Dual-Workspace Mode (Recommended)
- **Operator workspace**: Your custom operators (this can be anywhere)
- **TileLang source**: Separate checkout of the TileLang repository
- Configured via `TILELANG_SOURCE_PATH` environment variable
- Good for: Developing custom operators, proprietary kernels, performance research

This guide focuses on the **dual-workspace mode**.

## Directory Structure

### Recommended Layout

```
your-projects/
│
├── tilelang/                          # TileLang source (read-only for you)
│   ├── tilelang/
│   ├── src/
│   ├── examples/
│   └── ...
│
├── tilelang-operator-dev/             # This skill (installed once)
│   ├── scripts/
│   │   └── tilelang_operator_mcp.py  # MCP server
│   ├── resources/
│   │   └── tilelang_knowledge/       # Built-in knowledge base
│   └── ...
│
└── my-operators/                      # Your operator workspace! 👈
    ├── .mcp.json                      # MCP configuration
    ├── .env                            # TILELANG_SOURCE_PATH=../tilelang
    ├── .gitignore
    ├── README.md
    │
    ├── fused_moe/                      # Your first operator
    │   ├── operator.py
    │   ├── test_operator.py
    │   ├── benchmark.py
    │   └── README.md
    │
    ├── flash_attention_v2/             # Another operator
    │   └── ...
    │
    └── tilelang_knowledge/            # (Optional) Local knowledge overrides
        ├── patterns.jsonl              # Your custom patterns
        └── ...
```

## Step-by-Step Setup

### Prerequisites

1. Python 3.8+
2. Git
3. TileLang dependencies (PyTorch, CUDA, etc.)

### Step 1: Clone Repositories

```bash
# Clone TileLang source
git clone https://github.com/tile-ai/tilelang.git

# Clone the operator development skill
git clone https://github.com/Leafoon/tilelang-operator-dev.git

# Create your operator workspace (copy the template)
cp -r tilelang-operator-dev/resources/operator_template my-operators
```

### Step 2: Configure Environment

```bash
cd my-operators

# Copy and edit the environment file
cp .env.example .env

# Edit .env and set TILELANG_SOURCE_PATH
# Example:
# TILELANG_SOURCE_PATH=/home/user/your-projects/tilelang
```

### Step 3: Configure MCP Server

Edit `.mcp.json` to point to the MCP server location:

```json
{
  "mcpServers": {
    "tilelang-operator-knowledge": {
      "command": "python3",
      "args": [
        "/absolute/path/to/tilelang-operator-dev/scripts/tilelang_operator_mcp.py"
      ],
      "env": {
        "TILELANG_SOURCE_PATH": "/absolute/path/to/tilelang"
      }
    }
  }
}
```

**Relative path example** (if all repos are siblings):
```json
"args": ["${workspaceFolder}/../tilelang-operator-dev/scripts/tilelang_operator_mcp.py"],
"env": {
  "TILELANG_SOURCE_PATH": "${workspaceFolder}/../tilelang"
}
```

### Step 4: Validate Your Setup

```bash
# Test the MCP server directly
python3 /path/to/tilelang-operator-dev/scripts/tilelang_operator_mcp.py --check

# Expected output: status=passed with all checks green
```

### Step 5: Open in Claude Code

```bash
cd my-operators
claude .
```

Then ask:
> "Validate my workspace and show me the available operator capabilities"

## Environment Configuration

### Required Variables

| Variable | Description |
|----------|-------------|
| `TILELANG_SOURCE_PATH` | Path to your TileLang source checkout. Required for dual-workspace mode. |

### Optional Variables

| Variable | Description |
|----------|-------------|
| `PYTHONPATH` | Add TileLang to Python path if not installed via pip |
| `CUDA_VISIBLE_DEVICES` | Control which GPU(s) to use |

### .env File Example

```env
# TileLang source path (REQUIRED for dual-workspace)
TILELANG_SOURCE_PATH=/home/user/projects/tilelang

# Optional: Add TileLang to Python path
PYTHONPATH=${TILELANG_SOURCE_PATH}:${PYTHONPATH}

# Optional: GPU configuration
CUDA_VISIBLE_DEVICES=0
```

## MCP Configuration

The MCP server configuration is stored in `.mcp.json` in your workspace root.

### Configuration Fields

| Field | Description |
|-------|-------------|
| `command` | Python interpreter to use (python3 or python) |
| `args` | Path to `tilelang_operator_mcp.py` script |
| `env.TILELANG_SOURCE_PATH` | Path to TileLang source repository |

### Windows Configuration

Use `.mcp.windows.json` as your template - it uses `python` instead of `python3`:

```json
{
  "mcpServers": {
    "tilelang-operator-knowledge": {
      "command": "python",
      "args": [
        "${workspaceFolder}/../tilelang-operator-dev/scripts/tilelang_operator_mcp.py"
      ],
      "env": {
        "TILELANG_SOURCE_PATH": "${workspaceFolder}/../tilelang"
      }
    }
  }
}
```

## Creating New Operators

### Using the Setup Script

```bash
cd my-operators

# Create a new operator from template
python init_operator.py --tilelang ../tilelang --new-operator fused_moe
```

### Manual Creation

```bash
# Create directory
mkdir my_new_operator
cd my_new_operator

# Create required files
touch operator.py          # Your kernel implementation
touch test_operator.py     # Correctness tests
touch benchmark.py         # Performance benchmarks
touch README.md            # Documentation
```

### Operator Template

Use the `example_operator` as a starting point. It includes:

- `operator.py` - Template kernel with TileLang best practices
- `test_operator.py` - Pytest-based correctness tests
- `benchmark.py` - Performance comparison against reference
- `README.md` - Documentation template

## MCP Tools Available

All tools work in dual-workspace mode:

### Validation
- `inspect_tilelang_workspace` - Validate workspace configuration
- `validate_knowledge_base` - Check knowledge base integrity

### Search
- `search_capabilities` - Find relevant operator capabilities
- `search_patterns` - Look up implementation patterns
- `search_usage_patterns` - Find usage examples and workflows
- `lookup_apis` - Check TileLang API signatures
- `get_source_chunks` - Retrieve source code examples
- `trace_semantic_graph` - Explore code entity relationships

### Development
- `normalize_device_profile` - Get device-specific configuration
- `build_operator_retrieval_plan` - Create development plan
- `validate_operator_code` - Static analysis of your code
- `search_troubleshooting` - Find solutions to common issues
- `operator_development_wizard` - Step-by-step guided development

## Troubleshooting

### Issue: "TileLang source not found" error

**Solution:**
1. Check that `TILELANG_SOURCE_PATH` is set correctly in `.env`
2. Verify the path exists and contains TileLang source:
   ```bash
   ls $TILELANG_SOURCE_PATH/tilelang/__init__.py
   # Should exist
   ```
3. Restart Claude Code to pick up environment changes

### Issue: "Workspace validation fails"

**Solution:**
1. Run `inspect_tilelang_workspace` tool to see detailed errors
2. Check for missing required files:
   - `tilelang/__init__.py`
   - `tilelang/language/__init__.py`
3. Check for required directories:
   - `src/transform` or `src/op`
   - `examples/` or `testing/` or `docs/`

### Issue: MCP server won't start

**Solution:**
1. Check Python path in `.mcp.json`
2. Verify the path to `tilelang_operator_mcp.py` is correct
3. Test the server directly:
   ```bash
   python3 /path/to/tilelang_operator_mcp.py --check
   ```

### Issue: Knowledge base not found

**Solution:**
The skill includes a built-in knowledge base. If you see this error:
1. Verify the skill installation is complete
2. Check that `resources/tilelang_knowledge/` exists in the skill directory
3. Optionally, copy the knowledge base to your workspace for local modifications

## Getting Help

1. Run the self-check: `python scripts/tilelang_operator_mcp.py --check`
2. Use the `search_troubleshooting` tool for common issues
3. Check the [GitHub Issues](https://github.com/Leafoon/tilelang-operator-dev/issues)
4. Review examples in `examples/` directory

## Next Steps

1. ✅ Set up dual-workspace (this guide)
2. 🔍 Explore capabilities with `search_capabilities`
3. 📋 Review patterns with `search_patterns`
4. 🚀 Start coding using `operator_development_wizard`
5. ✅ Validate your code with `validate_operator_code`
6. 📊 Benchmark performance and iterate!
