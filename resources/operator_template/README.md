# TileLang Operator Optimization Workspace

This directory contains custom TileLang operators developed independently from the TileLang source repository.

## Directory Structure

```
operator_optimization/
├── .mcp.json              # MCP server configuration (only file needed!)
├── .gitignore             # Git ignore rules
├── README.md              # This file
│
├── fused_moe/             # Each operator has its own directory
│   ├── operator.py        # Operator implementation
│   ├── test_operator.py   # Correctness tests
│   ├── benchmark.py       # Performance benchmarks
│   └── README.md          # Operator documentation
│
├── flash_attention/       # Another operator
│   └── ...
│
└── tilelang_knowledge/    # (Optional) Local knowledge base overrides
    └── README.md
```

## Getting Started

**No configuration needed!** The MCP server automatically detects TileLang source by searching:

1. **Sibling directory**: `../tilelang/` (most common)
2. **Parent's sibling**: `../../tilelang/`
3. **Up to 3 parent levels**

### Quick Start

```bash
# 1. Open this directory in Claude Code
claude .

# 2. The server auto-detects TileLang source - just start coding!
#    Example: "develop a fused MoE operator for NVIDIA H100"
```

### Create a New Operator

```bash
python init_operator.py --new-operator my_new_operator
```

Or manually:

```bash
mkdir -p my_new_operator
touch my_new_operator/operator.py
touch my_new_operator/test_operator.py
touch my_new_operator/benchmark.py
touch my_new_operator/README.md
```

### List Existing Operators

```bash
python init_operator.py --list
```

## Auto-Detection

The MCP server automatically finds your TileLang source checkout. No `.env` file needed!

**Search priority:**
1. Explicit `tilelang_source_path` tool parameter (if provided)
2. `TILELANG_SOURCE_PATH` environment variable (if set)
3. **Auto-detect**: sibling `tilelang/` directory
4. **Auto-detect**: walk up to 3 parent levels
5. Fallback: current workspace (backward compatibility)

**Validation**: Only directories containing `tilelang/__init__.py` are considered valid.

## MCP Tools

When opening this workspace in Claude Code, the following tools are available:

- `inspect_tilelang_workspace` - Validate your setup (shows auto-detected path)
- `search_capabilities` - Find relevant TileLang capabilities
- `search_patterns` - Look up implementation patterns
- `lookup_apis` - Check TileLang API signatures
- `validate_operator_code` - Static analysis of your code
- `operator_development_wizard` - Step-by-step guidance

## Workflow

1. **Validate setup**: Run `inspect_tilelang_workspace` to confirm everything is configured
2. **Design**: Search capabilities and patterns for your operator type
3. **Implement**: Write your operator in `operator.py`
4. **Test**: Add tests in `test_operator.py`
5. **Benchmark**: Measure performance in `benchmark.py`
6. **Document**: Update `README.md` for each operator

## Tips

- Keep each operator focused on a single task
- Document performance improvements and trade-offs
- Use `tilelang_knowledge/` to add custom patterns specific to your operators
- Run the validation wizard after major changes

## Troubleshooting

**Q: "TileLang source not found" error**
A: Make sure `tilelang/` directory exists as a sibling of this workspace (or up to 3 levels above). If it's elsewhere, set `TILELANG_SOURCE_PATH` environment variable.

**Q: Multiple TileLang source candidates found**
A: Use the `tilelang_source_path` tool parameter to specify which one to use, or set `TILELANG_SOURCE_PATH` environment variable.

**Q: Knowledge base validation fails**
A: The skill uses built-in knowledge base by default. You can also copy the knowledge base to `tilelang_knowledge/` for local overrides.
