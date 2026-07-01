---
name: run-tilelang-mcp
description: Run, test, and verify the TileLang MCP server. Smoke-test all 13 tools, call individual tools, list available tools. Use when testing or debugging the tilelang-operator-dev skill's MCP server.
---

# Run TileLang MCP Server

The TileLang MCP server (`scripts/tilelang_operator_mcp.py`) is a stdio-based JSON-RPC server that provides 13 tools for TileLang operator development: workspace validation, knowledge base validation, device normalization, capability/pattern/usage search, API lookup, source chunk retrieval, semantic graph tracing, retrieval plan building, troubleshooting search, code validation, and development wizard.

**Driver:** `.claude/skills/run-tilelang-mcp/driver.py`

## Prerequisites

- Python 3.8+ (use `python`, not `python3` on Windows — the `python3` alias is the Windows Store stub)
- No external dependencies — pure stdlib

## Smoke Test

Exercises all 13 tools in one pass. The server automatically uses the built-in knowledge base from `resources/tilelang_knowledge/` when the workspace doesn't have its own copy.

```bash
cd <repo-root>
python .claude/skills/run-tilelang-mcp/driver.py --smoke
```

Add `--verbose` to see full output for passing tools too.

## List Tools

```bash
python .claude/skills/run-tilelang-mcp/driver.py --list
```

## Call a Single Tool

```bash
python .claude/skills/run-tilelang-mcp/driver.py --call normalize_device_profile --args '{"vendor":"nvidia","model":"H100","target":"cuda"}'
python .claude/skills/run-tilelang-mcp/driver.py --call inspect_tilelang_workspace
python .claude/skills/run-tilelang-mcp/driver.py --call search_capabilities --args '{"query":"gemm"}'
```

## Direct Server Check

The server has a built-in self-check that prints server info JSON and exits:

```bash
python scripts/tilelang_operator_mcp.py --check
```

## Raw JSON-RPC (manual)

```bash
printf '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}\n{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}\n' | python scripts/tilelang_operator_mcp.py
```

## Gotchas

- **`python3` on Windows** — the `python3` alias is the Windows Store stub that exits with code 49. Always use `python` on Windows.
- **Built-in knowledge base** — the server falls back to `resources/tilelang_knowledge/` when the workspace doesn't have its own copy. All 13 tools work from the skill repo without copying anything.
- **Device normalization** — known models such as H100 can be recognized without an explicit vendor, but include `vendor`, `model`, and optionally `target` for best results on less common hardware.
- **Server is single-shot** — each invocation processes one batch of JSON-RPC messages from stdin then exits. It's not a long-running server.
