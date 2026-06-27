---
name: run-tilelang-mcp
description: Use when developing, adapting, explaining, or validating TileLang operators. Provides MCP-backed knowledge retrieval, device-aware planning, and guided workflows. The MCP server auto-detects TileLang source from sibling/parent directories.
---

# TileLang Operator Dev

Use this skill when the user asks to develop, adapt, explain, or validate TileLang operators (GEMM, attention, reduction, convolution, elementwise, etc.).

The MCP server (`tilelang-operator-knowledge`) provides 13 tools for structured operator development. It automatically detects the TileLang source repository by searching sibling and parent directories — no configuration needed.

## Quick Start

1. Call `inspect_tilelang_workspace` to validate the setup
2. Call `validate_knowledge_base` to confirm knowledge files
3. Use the wizard: `operator_development_wizard` with `current_step: 1`

## Available MCP Tools

| Tool | Purpose |
|------|---------|
| `inspect_tilelang_workspace` | Validate TileLang repo + knowledge base |
| `validate_knowledge_base` | Check JSON/JSONL delivery files |
| `normalize_device_profile` | Normalize vendor/model/target |
| `search_capabilities` | Find operator capability categories |
| `search_patterns` | Find implementation patterns |
| `search_usage_patterns` | Find example workflows |
| `lookup_apis` | Check API signatures |
| `get_source_chunks` | Get source code reference chunks |
| `trace_semantic_graph` | Trace dependency graph |
| `build_operator_retrieval_plan` | Build a complete retrieval plan |
| `search_troubleshooting` | Find solutions for common errors |
| `validate_operator_code` | Static analysis of generated code |
| `operator_development_wizard` | 12-step guided workflow |

## Standard Workflow

1. **Validate** — `inspect_tilelang_workspace` + `validate_knowledge_base`
2. **Device** — `normalize_device_profile` with user's hardware
3. **Search** — `search_capabilities` → `search_patterns` → `search_usage_patterns`
4. **APIs** — `lookup_apis` for required symbols
5. **Source** — `get_source_chunks` if patterns need more detail
6. **Plan** — `build_operator_retrieval_plan`
7. **Implement** — Generate code (the ONLY step that writes code)
8. **Validate** — `validate_operator_code`
9. **Troubleshoot** — `search_troubleshooting` if errors occur

## Supported Devices

- NVIDIA: A100 (sm_80), H100 (sm_90), B100 (sm_100a)
- AMD: MI300X/MI350 (gfx940/gfx950)
- CPU: llvm, c
- Apple Silicon: metal
- WebGPU: webgpu

## Hard Stop Conditions

Stop immediately when:
- TileLang source repository not found
- Knowledge base files missing
- JSON/JSONL parsing fails

## Tips

- Always validate workspace before generating code
- Use `operator_development_wizard` for guided step-by-step workflow
- Device-specific features (WGMMA, TMA, MFMA) require architecture verification
- The MCP server uses built-in knowledge base — no need to copy knowledge files
