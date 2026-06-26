# TileLang Operator Optimization Workspace

This directory contains custom TileLang operators developed independently from the TileLang source repository.

## Directory Structure

```
operator_optimization/
├── .mcp.json              # MCP server configuration
├── .env                   # Environment configuration (copy from .env.example)
├── .env.example           # Environment template
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

### 1. Set up Environment

Copy the example env file and configure paths:

```bash
cp .env.example .env
# Edit .env and set TILELANG_SOURCE_PATH to your TileLang checkout
```

Example `.env`:
```env
TILELANG_SOURCE_PATH=/home/user/projects/tilelang
```

### 2. Create a New Operator

```bash
mkdir -p my_new_operator
touch my_new_operator/operator.py
touch my_new_operator/test_operator.py
touch my_new_operator/benchmark.py
touch my_new_operator/README.md
```

### 3. Use the MCP Tools

When opening this workspace in Claude Code, the following tools are available:

- `inspect_tilelang_workspace` - Validate your setup
- `search_capabilities` - Find relevant TileLang capabilities
- `search_patterns` - Look up implementation patterns
- `lookup_apis` - Check TileLang API signatures
- `validate_operator_code` - Static analysis of your code
- `operator_development_wizard` - Step-by-step guidance

### 4. Workflow

1. **Validate setup**: Run `inspect_tilelang_workspace` to confirm everything is configured
2. **Design**: Search capabilities and patterns for your operator type
3. **Implement**: Write your operator in `operator.py`
4. **Test**: Add tests in `test_operator.py`
5. **Benchmark**: Measure performance in `benchmark.py`
6. **Document**: Update `README.md` for each operator

## Modes of Operation

### Single-Workspace Mode (Legacy)
- Operator code lives inside the TileLang source repo
- `TILELANG_SOURCE_PATH` is not required (defaults to workspace)

### Dual-Workspace Mode (Recommended)
- **This directory**: Your operator optimization code
- **TileLang source**: Separate checkout of TileLang
- Configured via `TILELANG_SOURCE_PATH` environment variable

## Tips

- Keep each operator focused on a single task
- Document performance improvements and trade-offs
- Use `tilelang_knowledge/` to add custom patterns specific to your operators
- Run the validation wizard after major changes

## Troubleshooting

**Q: "TileLang source not found" error**
A: Make sure `TILELANG_SOURCE_PATH` in `.env` points to a valid TileLang checkout

**Q: Knowledge base validation fails**
A: The skill uses built-in knowledge base by default. You can also copy the knowledge base to `tilelang_knowledge/` for local overrides.

**Q: How to use a custom knowledge base**
A: Copy `tilelang_knowledge/` from tilelang-operator-dev to this workspace and modify as needed.
