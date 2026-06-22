# TileLang Operator Dev

MCP-backed TileLang operator development skill with workspace validation and device-aware planning.

## Installation

### Universal (Any MCP-compatible tool)

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/tilelang-operator-dev.git
   ```

2. Copy skill files to your AI tool's skill directory:
   ```bash
   # For Claude Code
   cp -r tilelang-operator-dev ~/.claude/skills/

   # For other tools, copy SKILL.md to appropriate location
   ```

3. Copy MCP config and knowledge base to your TileLang workspace:
   ```bash
   cp tilelang-operator-dev/resources/.mcp.json your-workspace/
   cp -r tilelang-operator-dev/resources/tilelang_knowledge your-workspace/
   ```

4. Update the path in `.mcp.json` to point to the actual location of `scripts/tilelang_operator_mcp.py`.

### Tool-Specific Notes

| Tool | Skill Location | MCP Config |
|------|----------------|------------|
| Claude Code | `~/.claude/skills/tilelang-operator-dev/` | `.mcp.json` in project root |
| OpenAI Codex | `.codex-plugin/` | `.mcp.json` in project root |
| Cursor | `.cursorrules` or project root | `.mcp.json` in project root |
| OpenCode | Project config | `.mcp.json` in project root |

## Project Structure

```
tilelang-operator-dev/
├── SKILL.md                         # Core skill instructions
├── metadata.json                    # Skill metadata
├── README.md                        # This file
├── CHANGELOG.md                     # Version history
├── LICENSE                          # Apache-2.0
├── .gitignore
│
├── scripts/                         # Executable scripts
│   └── tilelang_operator_mcp.py     # MCP server
│
├── resources/                       # Resource files
│   ├── .mcp.json                    # MCP configuration
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
    ├── test_cases.md
    └── eval.yaml
```

## What Each File Does

| File | Purpose | Who Reads It |
|------|---------|--------------|
| `SKILL.md` | AI agent instructions (when/how to use tools) | AI agent (Claude, GPT, etc.) |
| `metadata.json` | Skill metadata (version, author, etc.) | AI tools, package managers |
| `scripts/tilelang_operator_mcp.py` | MCP server implementation | AI tool runtime |
| `resources/.mcp.json` | MCP server connection config | AI tools (Claude Code, Codex, etc.) |
| `resources/tilelang_knowledge/` | Pre-generated knowledge base | MCP server |
| `examples/` | Usage examples | Developers |
| `tests/` | Test cases and eval config | CI/CD, developers |

## MCP Tools

The MCP server provides these tools:

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

### Running the MCP Server

```bash
python3 scripts/tilelang_operator_mcp.py --check
```

### Testing

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python3 scripts/tilelang_operator_mcp.py
```

### Running Tests

See `tests/test_cases.md` for manual test cases. Automated testing coming soon.

## License

Apache-2.0
