# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

### Added
- Added constrained recognition for Huawei Ascend, MetaX/Muxi, Moore Threads, Cambricon, Biren, Iluvatar, and Baidu Kunlun device profiles.
- Added English troubleshooting fields to `troubleshooting.jsonl` and exposed them through `search_troubleshooting`.
- Added a troubleshooting record for unsupported or unverified accelerator vendor targets.
- Added source evidence auditing to `validate_knowledge_base` when a valid TileLang checkout is resolved.
- Added usage records for split-K GEMM, sparse GEMM, flash/decode attention, convolution autotune, elementwise, top-k, and fused MoE pattern links.
- Added audit checks for `patterns.jsonl` references to missing `usage_patterns.jsonl` IDs.

### Changed
- Expanded English and Chinese README usage guidance with Claude Code startup commands, global and workspace-local setup flows, prompt structures, and expected Skill behavior.
- Clarified in README and Skill instructions that non-CUDA/HIP/CPU/Metal/WebGPU accelerator targets must not be inferred without local TileLang backend evidence, with Huawei Ascend requiring external `tilelang-ascend` evidence when using the main TileLang checkout.
- Added `validate_operator_code` warnings for unverified vendor targets such as CANN, MUSA, MACA, MLU, and XPU.
- Included workspace/source/knowledge trace fields directly in `build_operator_retrieval_plan` output.
- Reduced `SETUP_GUIDE.md` duplication so README remains the authoritative setup and usage guide.
- Updated project and template MCP configs to use `${CLAUDE_PROJECT_DIR:-.}` instead of the unsupported `${workspaceFolder}` variable.
- Updated `setup.sh` to upsert the user-scoped MCP server in `~/.claude.json`.

### Fixed
- Kept `build_operator_retrieval_plan` constrained whenever device normalization is constrained.
- Clarified `get_source_chunks` tool wording so it does not imply live source-file reads.
- Made the operator template tests skip cleanly when PyTorch or CUDA is unavailable.
- Kept `validate_knowledge_base` and `build_operator_retrieval_plan` from reporting success when TileLang source cannot be resolved.
- Fixed CPU device normalization for Intel Xeon and AMD EPYC so CPU requests are not routed to unknown or HIP targets.
- Updated stale examples to match dual-workspace and bundled-knowledge behavior.

## [0.4.3] - 2026-07-01

### Changed
- Made `tilelang-operator-dev` the default Claude Code operator development skill installed by `setup.sh`.
- Updated README and setup guide with professional global and workspace-local Claude Code configuration modes.
- Replaced the operator template's `run-tilelang-mcp` skill entrypoint with a lightweight `tilelang-operator-dev` entrypoint.
- Clarified dual-workspace behavior and bundled knowledge-base fallback in the main skill instructions.
- Made `setup.sh` merge `tilelang-operator-knowledge` into existing Claude Code MCP config instead of overwriting other configured servers.
- Made `setup.sh` require Python 3.10+ and honor `PYTHON=/path/to/python3.10` when writing MCP config.
- Made `troubleshooting.jsonl` part of the validated knowledge delivery set and local knowledge override path.
- Updated the operator workspace template to use official TileLang GEMM syntax and tile-aligned tests.
- Removed the default workspace-local `tilelang_knowledge/` placeholder from the operator template; bundled knowledge is the default.
- Synced root, repository-local, and template-local `tilelang-operator-dev` skill entrypoints.
- Added targeted and index-style knowledge patterns so all first-level official TileLang `examples/` directories have a retrieval entry.
- Added `scripts/audit_tilelang_knowledge.py` to audit knowledge records against a TileLang source checkout.
- Updated MCP tool descriptions and evaluation docs to reflect bundled knowledge fallback and capability-to-pattern filtering.

### Fixed
- Fixed `operator_development_wizard` step 1 auto-validation so it no longer calls a missing function when `workspace_path` is provided.
- Added a regression test for wizard step 1 with `workspace_path`.
- Fixed `operator_development_wizard` step 1 auto-validation to preserve explicit `tilelang_source_path`.
- Fixed `search_patterns(capability_id=...)` to resolve pattern IDs through `capability_map.related_patterns`.
- Fixed `build_operator_retrieval_plan` so common GEMM intents return pattern candidates.
- Fixed `search_troubleshooting` to use workspace-local knowledge when a complete local delivery set is present.
- Fixed `lookup_apis` ranking for `T.*` and `tl.*` symbol aliases so exact API records rank above docstring-only matches.
- Reduced false positives in `validate_operator_code` by recognizing `from tilelang import language as T` and limiting anti-pattern checks to TileLang kernel functions.
- Fixed `resources/operator_template/init_operator.py` to support explicit `--tilelang-source` and `TILELANG_SOURCE_PATH`.
- Fixed template examples and `init_operator.py` copying to avoid Python stdlib `operator` import confusion and local cache artifacts.
- Extended the knowledge audit script to validate nested `evidence[].line` entries.

## [0.4.2] - 2026-06-27

### Fixed
- **Skill discovery in operator template**: Added `.claude/skills/run-tilelang-mcp/SKILL.md` to `resources/operator_template/` so Claude Code discovers the skill when opening an operator workspace created from the template. Previously, only MCP tools were available but the skill instructions were missing.
- **Knowledge base fallback**: `knowledge_dir()` now correctly falls back to built-in knowledge when local `tilelang_knowledge/` directory exists but is missing required files (e.g., template placeholder with only README.md).

### Added
- **`setup.sh`**: One-command setup script that installs Skill and MCP config to the parent directory, enabling Claude Code to discover the skill from any workspace.
- **Root `.mcp.json`**: Added MCP config to repo root so `tilelang-operator-dev/` works as a standalone workspace.
- **Usage Examples**: Added concrete question examples to README for GEMM, attention, device-specific, and troubleshooting scenarios.

## [0.4.1] - 2026-06-26

### Added
- **Smart Auto-Detection**: MCP server automatically finds TileLang source repository
  - Searches sibling `tilelang/` directory first
  - Walks up to 3 parent levels looking for `tilelang/`
  - Validates candidates by checking `tilelang/__init__.py`
  - Reports multiple candidates when found, lets user choose
  - Zero configuration needed for common directory layouts

### Removed
- `.env.example` template - no longer needed with auto-detection
- `--tilelang` parameter from `init_operator.py` - auto-detection handles this

### Simplified
- `operator_template/.mcp.json` - removed `env` block (no more `TILELANG_SOURCE_PATH` needed)
- `operator_template/README.md` - updated to reflect zero-config workflow

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
