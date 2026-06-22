# Changelog

All notable changes to this project will be documented in this file.

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
