# Changelog

All notable changes to this project will be documented in this file.

## [0.4.0] - 2026-06-26

### Added
- **Dual-Workspace Mode**: Support for independent operator development separate from TileLang source
  - New `tilelang_source_root()` function to resolve TileLang source path via `TILELANG_SOURCE_PATH` env var
  - New `tilelang_source_path` tool parameter for explicit TileLang source configuration
  - New `operator_workspace_path` and `workspace_mode` ("single" or "dual") in tool responses
  - Helpful hint messages when TileLang source is not configured correctly

- **Operator Workspace Template**: Complete template for independent operator development
  - `resources/operator_template/` with example operator structure
  - `.env.example` for easy environment configuration
  - Pre-configured `.mcp.json` for MCP server integration
  - Example operator with test and benchmark templates
  - `.gitignore` optimized for operator development

- **Setup Utility**: `init_operator.py` script to:
  - Validate TileLang source checkout
  - Create new operators from template
  - List existing operators in workspace
  - Auto-configure `.env` file

### Updated
- MCP server tools now support dual-workspace mode:
  - `inspect_tilelang_workspace` - validates workspace with new field returns
  - `validate_knowledge_base` - supports operator workspace + TileLang source separation
  - All search tools (`search_capabilities`, `search_patterns`, etc.) support the new param
- `README.md` updated with independent operator development instructions
- MCP configuration template with dual-workspace mode documentation

### Breaking Changes
- None - fully backward compatible. Default behavior unchanged when `TILELANG_SOURCE_PATH` is not set.

## [0.3.0] - 2026-06-22

### Added
- Initial release as a standard skill package
- MCP server for TileLang workspace validation and knowledge retrieval
- Pre-generated `tilelang_knowledge/` with capability map, patterns, APIs, and semantic graph
- Device-aware planning for NVIDIA, AMD, CPU, Apple Silicon, and WebGPU
- Support for multiple MCP-compatible tools (Claude Code, Codex, Cursor, OpenCode)

### Changed
- Restructured as standard skill format with metadata.json, examples/, resources/, tests/
- Unified MCP configuration format for cross-tool compatibility

## [0.2.0] - 2026-04-24

### Added
- Codex plugin format support
- Device profile normalization
- Semantic graph tracing

### Changed
- Improved search scoring with capability keyword boosting

## [0.1.0] - 2026-04-01

### Added
- Initial MCP server implementation
- Basic workspace validation
- Pattern and API search
