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

此技能需要一个 **TileLang 工作区** — AI 代理会在生成代码前验证工作区。你需要以下之一：

**方案 A：克隆官方 TileLang 仓库**（推荐用于学习/贡献）

```bash
git clone https://github.com/tile-ai/tilelang.git
cd tilelang
```

**方案 B：你自己的 TileLang 项目**（用于构建自定义算子）

```bash
pip install tilelang
mkdir my-project && cd my-project
```

没有有效的 TileLang 工作区，技能会停止并拒绝生成代码。

### 安装

#### 一键安装（推荐）

```bash
# 1. 克隆两个仓库到任意目录
mkdir my-tilelang-projects && cd my-tilelang-projects
git clone https://github.com/Leafoon/tilelang-operator-dev.git
git clone https://github.com/tile-ai/tilelang.git

# 2. 运行安装脚本 — 将 Skill 和 MCP 配置安装到全局
cd tilelang-operator-dev && bash setup.sh && cd ..

# 3. 创建算子工作区（只放算子文件）
mkdir my-operators

# 4. 在任意目录启动 Claude Code：
claude .                        # ← 父目录
claude tilelang-operator-dev    # ← 技能仓库
claude my-operators             # ← 你的算子工作区
```

`setup.sh` 脚本将 Skill 安装到 `~/.claude/skills/`，MCP 配置安装到 `~/.claude/`，因此从任意目录均可使用。

#### 手动安装

```bash
git clone https://github.com/Leafoon/tilelang-operator-dev.git
git clone https://github.com/tile-ai/tilelang.git

# 全局安装 skill
cp -r tilelang-operator-dev/.claude/skills/run-tilelang-mcp ~/.claude/skills/

# 全局安装 MCP 配置（需编辑路径）
cp tilelang-operator-dev/resources/.mcp.json ~/.claude/.mcp.json
```

> **Windows 用户：** 使用 `.mcp.windows.json` 代替 — 它用 `python` 而非 `python3`。

> **注意：** 知识库已内置在 MCP 服务器中 — 不需要单独复制 `tilelang_knowledge/`。服务器会自动使用技能包中的 `resources/tilelang_knowledge/` 作为回退。

#### 其他 MCP 兼容工具

| 工具 | 技能位置 | MCP 配置 |
|------|----------|----------|
| Claude Code | `.claude/skills/` 或 `~/.claude/skills/` | 项目根目录的 `.mcp.json` |
| OpenAI Codex | `.codex-plugin/` | 项目根目录的 `.mcp.json` |
| Cursor | `.cursorrules` 或项目根目录 | 项目根目录的 `.mcp.json` |
| OpenCode | 项目配置 | 项目根目录的 `.mcp.json` |

### 使用示例

安装完成后，在任意目录打开 Claude Code，可以这样提问：

#### GEMM 算子

- `写一个 NVIDIA H100 的基础 GEMM 算子，fp16 输入`
- `开发一个 split-K GEMM 算子，用于大 K 维度`
- `为 A100 创建 2:4 稀疏 GEMM 算子`
- `写一个 Hopper 的 int4 反量化 GEMM 算子`
- `构建一个 MoE 风格的分组 GEMM 算子`

#### Attention 算子

- `实现一个 H100 的 flash attention 前向算子`
- `写一个带分页 KV 缓存的 GQA decode attention 算子`
- `为 DeepSeek 模型创建 MLA decode 算子`

#### 设备适配

- `写一个能在 Apple M4 上运行的 GEMM 算子，使用 Metal 后端`
- `为 AMD MI300X 创建 elementwise add 算子`
- `为 NVIDIA B100 Blackwell 架构开发 GEMM 算子`

#### 归约与其他

- `实现一个 online softmax 算子`
- `写一个 RMSNorm 算子`
- `创建一个 Top-K 选择算子`
- `用 im2col 构建 2D 卷积算子`

#### 代码验证与故障排查

- `验证这段 TileLang 算子代码`（粘贴代码）
- `我的 WGMMA 在 A100 上编译报错，帮我修复`
- `为什么我的 AMD 算子输出结果不正确？`

#### 引导式开发

- `一步步指导我开发一个 GEMM 算子`
- `帮我把 H100 的算子适配到 A100`

### MCP 工具

MCP 服务器提供 **13 个工具**用于 TileLang 算子开发：

| 工具 | 描述 |
|------|------|
| `inspect_tilelang_workspace` | 验证 TileLang 仓库和知识库 |
| `validate_knowledge_base` | 解析和验证 JSON/JSONL 交付文件 |
| `normalize_device_profile` | 标准化供应商/型号/目标 |
| `search_capabilities` | 搜索 capability_map.json 查找算子能力 |
| `search_patterns` | 搜索 patterns.jsonl 查找实现模式 |
| `search_usage_patterns` | 搜索 usage_patterns.jsonl 查找工作流示例 |
| `lookup_apis` | 搜索 apis.jsonl 查找 API 符号和签名 |
| `get_source_chunks` | 获取源码回退片段 |
| `trace_semantic_graph` | 追踪语义图节点和边 |
| `build_operator_retrieval_plan` | 构建结构化检索计划 |
| `search_troubleshooting` | 搜索故障排查知识库 |
| `validate_operator_code` | 对生成代码进行静态分析 |
| `operator_development_wizard` | 12 步引导式开发工作流 |

### 标准工作流

1. **工作区验证** - `inspect_tilelang_workspace`
2. **知识库验证** - `validate_knowledge_base`
3. **设备标准化** - `normalize_device_profile`
4. **能力搜索** - `search_capabilities`
5. **模式搜索** - `search_patterns`
6. **使用模式搜索** - `search_usage_patterns`
7. **API 确认** - `lookup_apis`
8. **源码回退** - `get_source_chunks`
9. **依赖追踪** - `trace_semantic_graph`
10. **检索计划** - `build_operator_retrieval_plan`
11. **实现** - 生成代码（唯一生成代码的步骤）
12. **代码验证** - `validate_operator_code`
13. **故障排查** - `search_troubleshooting`（如果出现错误）

### 开发

#### 运行 MCP 服务器

```bash
python scripts/tilelang_operator_mcp.py --check
```

#### 冒烟测试（全部 13 个工具）

```bash
python .claude/skills/run-tilelang-mcp/driver.py --smoke
```

#### 运行测试

```bash
python -m pytest tests/test_mcp_server.py -v
```

### 文档

| 文档 | 描述 |
|------|------|
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | 详细设置指南 |
| [CHANGELOG.md](CHANGELOG.md) | 版本历史 |
| [SKILL.md](SKILL.md) | AI 代理的核心技能指令 |
| [examples/](examples/) | 使用示例 |
| [tests/](tests/) | 测试用例 |

### 许可证

Apache-2.0
