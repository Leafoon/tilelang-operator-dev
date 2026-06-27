# TileLang Operator Dev

**English** | [中文](#中文)

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
```

Without a valid TileLang workspace, the skill will stop and refuse to generate code.

## Installation

### One-Command Setup (Recommended)

```bash
# 1. Clone both repos into any directory
mkdir my-tilelang-projects && cd my-tilelang-projects
git clone https://github.com/Leafoon/tilelang-operator-dev.git
git clone https://github.com/tile-ai/tilelang.git

# 2. Run setup — installs Skill and MCP config globally
cd tilelang-operator-dev && bash setup.sh && cd ..

# 3. Create your operator workspace (only operator files)
mkdir my-operators

# 4. Open Claude Code from any directory:
claude .                        # ← parent directory
claude tilelang-operator-dev    # ← skill repo
claude my-operators             # ← your operator workspace
```

The `setup.sh` script installs the Skill to `~/.claude/skills/` and MCP config to `~/.claude/`, so it works from any directory.

### Manual Setup

```bash
git clone https://github.com/Leafoon/tilelang-operator-dev.git
git clone https://github.com/tile-ai/tilelang.git

# Install skill globally
cp -r tilelang-operator-dev/.claude/skills/run-tilelang-mcp ~/.claude/skills/

# Install MCP config globally (adjust path)
cp tilelang-operator-dev/resources/.mcp.json ~/.claude/.mcp.json
# Edit ~/.claude/.mcp.json — set the script path to the actual location
```

> **Windows users:** use `.mcp.windows.json` instead — it uses `python` instead of `python3`.

### Other MCP-compatible Tools

| Tool | Skill Location | MCP Config |
|------|----------------|------------|
| Claude Code | `.claude/skills/` or `~/.claude/skills/` | `.mcp.json` in project root |
| OpenAI Codex | `.codex-plugin/` | `.mcp.json` in project root |
| Cursor | `.cursorrules` or project root | `.mcp.json` in project root |
| OpenCode | Project config | `.mcp.json` in project root |

## Usage Examples

After setup, open Claude Code and ask questions like:

### GEMM Operators

- `Write a basic GEMM kernel for NVIDIA H100 with fp16 inputs`
- `Develop a split-K GEMM operator for large K dimensions`
- `Create a 2:4 sparse GEMM kernel for A100`
- `Write a dequantized int4 GEMM kernel for Hopper`
- `Build a grouped GEMM (MoE-style) operator for multiple experts`

### Attention Operators

- `Implement a flash attention forward kernel for H100`
- `Write a GQA decode attention kernel with paged KV cache`
- `Create an MLA decode kernel for DeepSeek-style models`

### Device-Specific

- `Write a GEMM kernel that runs on Apple M4 with Metal backend`
- `Create an elementwise add operator for AMD MI300X`
- `Develop a GEMM for NVIDIA B100 Blackwell architecture`

### Reductions & Others

- `Implement an online softmax kernel`
- `Write an RMSNorm operator`
- `Create a Top-K selection kernel`
- `Build a 2D convolution operator using im2col`

### Code Validation & Troubleshooting

- `Validate this TileLang operator code` (paste your code)
- `I'm getting a compilation error with WGMMA on my A100 — help me fix it`
- `Why is my kernel producing incorrect results on AMD?`

### Guided Workflow

- `Walk me through developing a GEMM kernel step by step`
- `Help me adapt my H100 kernel to work on A100`

## MCP Tools

The MCP server provides **13 tools** for TileLang operator development:

| Tool | Description |
|------|-------------|
| `inspect_tilelang_workspace` | Validate TileLang repository and knowledge base |
| `validate_knowledge_base` | Parse and validate JSON/JSONL delivery files |
| `normalize_device_profile` | Normalize vendor/model/target |
| `search_capabilities` | Search capability_map.json for operator capabilities |
| `search_patterns` | Search patterns.jsonl for implementation patterns |
| `search_usage_patterns` | Search usage_patterns.jsonl for example workflows |
| `lookup_apis` | Search apis.jsonl for API symbols and signatures |
| `get_source_chunks` | Retrieve source fallback chunks |
| `trace_semantic_graph` | Trace semantic graph nodes and edges |
| `build_operator_retrieval_plan` | Build a structured retrieval plan |
| `search_troubleshooting` | Search troubleshooting knowledge base |
| `validate_operator_code` | Static analysis of generated code |
| `operator_development_wizard` | 12-step guided workflow |

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
11. **Implementation** - Generate code (the ONLY step that writes code)
12. **Code Validation** - `validate_operator_code`
13. **Troubleshooting** - `search_troubleshooting` (if errors occur)

## Development

### Running the MCP Server

```bash
python scripts/tilelang_operator_mcp.py --check
```

### Smoke Test (all 13 tools)

```bash
python .claude/skills/run-tilelang-mcp/driver.py --smoke
```

### Running Tests

```bash
python -m pytest tests/test_mcp_server.py -v
```

## Documentation

| Document | Description |
|----------|-------------|
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | Detailed setup guide |
| [CHANGELOG.md](CHANGELOG.md) | Version history |
| [SKILL.md](SKILL.md) | Core skill instructions for AI agents |
| [examples/](examples/) | Usage examples |
| [tests/](tests/) | Test cases |

## License

Apache-2.0

---

## 中文

**[English](#tilelang-operator-dev)** | **中文**

MCP 驱动的 TileLang 算子开发技能，支持工作区验证、设备感知规划和智能自动检测。

### 特性

- 🔍 **智能自动检测** - 自动查找 TileLang 源码仓库（零配置）
- 🔄 **双工作区模式** - 独立于 TileLang 源码开发算子
- 📚 **内置知识库** - 13 个 MCP 工具，包含预生成的模式、API 和示例
- 🎯 **设备感知规划** - 支持 NVIDIA、AMD、CPU、Apple Silicon 和 WebGPU
- ✅ **验证优先** - 生成代码前强制进行工作区验证
- 🛠️ **开发向导** - 分步引导式算子开发工作流

### 前置条件

此技能需要一个 **TileLang 工作区**。你需要以下之一：

```bash
# 方案 A：克隆官方 TileLang 仓库
git clone https://github.com/tile-ai/tilelang.git

# 方案 B：pip 安装
pip install tilelang
```

### 安装

```bash
# 1. 克隆两个仓库
mkdir my-tilelang-projects && cd my-tilelang-projects
git clone https://github.com/Leafoon/tilelang-operator-dev.git
git clone https://github.com/tile-ai/tilelang.git

# 2. 运行安装脚本
cd tilelang-operator-dev && bash setup.sh && cd ..

# 3. 创建算子工作区（只放算子文件）
mkdir my-operators

# 4. 启动 Claude Code
claude .
```

### 使用示例

**GEMM 算子：**
- `写一个 NVIDIA H100 的基础 GEMM 算子，fp16 输入`
- `为 A100 创建 2:4 稀疏 GEMM 算子`
- `构建一个 MoE 风格的分组 GEMM 算子`

**Attention 算子：**
- `实现一个 H100 的 flash attention 前向算子`
- `写一个带分页 KV 缓存的 GQA decode attention 算子`

**设备适配：**
- `写一个能在 Apple M4 上运行的 GEMM 算子，使用 Metal 后端`
- `为 AMD MI300X 创建 elementwise add 算子`

**其他：**
- `实现一个 online softmax 算子`
- `写一个 RMSNorm 算子`
- `一步步指导我开发一个 GEMM 算子`

### 许可证

Apache-2.0
