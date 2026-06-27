# TileLang Operator Dev

**English** | [中文](#中文)

A Claude Code skill for TileLang operator development, powered by an MCP server with 13 tools for workspace validation, knowledge retrieval, device-aware planning, and code validation.

## Features

- **Smart Auto-Detection** — Automatically locates TileLang source repository (zero configuration)
- **Dual-Workspace Mode** — Develop operators in a separate directory from TileLang source
- **Built-in Knowledge Base** — Pre-generated patterns, APIs, usage workflows, and source chunks
- **Device-Aware Planning** — Supports NVIDIA, AMD, CPU, Apple Silicon, and WebGPU
- **Validation-First Workflow** — Mandatory workspace and knowledge validation before code generation
- **Development Wizard** — 12-step guided workflow from intent to validated code

## Prerequisites

- Python 3.8+
- Claude Code
- A TileLang source repository (cloned or pip-installed)

The skill validates the workspace before generating any code. Without a valid TileLang workspace, it stops and refuses to proceed.

## Installation

### Quick Start

```bash
# Clone
git clone https://github.com/Leafoon/tilelang-operator-dev.git
git clone https://github.com/tile-ai/tilelang.git

# Install skill and MCP config globally
cd tilelang-operator-dev && bash setup.sh && cd ..

# Create your operator workspace
mkdir my-operators

# Restart Claude Code, then:
cd my-operators && claude .
```

The `setup.sh` script installs:
- Skill to `~/.claude/skills/run-tilelang-mcp/`
- MCP config to `~/.claude/.mcp.json`

After restart, Claude Code discovers the skill from any directory.

### Manual Installation

```bash
# Skill
mkdir -p ~/.claude/skills/run-tilelang-mcp
cp tilelang-operator-dev/.claude/skills/run-tilelang-mcp/SKILL.md ~/.claude/skills/run-tilelang-mcp/

# MCP config (edit the script path)
cat > ~/.claude/.mcp.json << 'EOF'
{
  "mcpServers": {
    "tilelang-operator-knowledge": {
      "command": "python3",
      "args": ["/path/to/tilelang-operator-dev/scripts/tilelang_operator_mcp.py"]
    }
  }
}
EOF
```

### Windows

The MCP server uses `python3` by default. On Windows, use `python` instead:

```json
{
  "mcpServers": {
    "tilelang-operator-knowledge": {
      "command": "python",
      "args": ["C:\\path\\to\\tilelang-operator-dev\\scripts\\tilelang_operator_mcp.py"]
    }
  }
}
```

## Usage

Open Claude Code in your operator directory and ask questions directly. The skill auto-invokes when it detects a TileLang operator development request.

### Examples

**GEMM Operators**
- Write a basic GEMM kernel for NVIDIA H100 with fp16 inputs
- Develop a split-K GEMM operator for large K dimensions
- Create a 2:4 sparse GEMM kernel for A100
- Build a grouped GEMM (MoE-style) operator for multiple experts

**Attention Operators**
- Implement a flash attention forward kernel for H100
- Write a GQA decode attention kernel with paged KV cache
- Create an MLA decode kernel for DeepSeek-style models

**Device Adaptation**
- Write a GEMM kernel that runs on Apple M4 with Metal backend
- Create an elementwise add operator for AMD MI300X
- Develop a GEMM for NVIDIA B100 Blackwell architecture

**Reductions & Others**
- Implement an online softmax kernel
- Write an RMSNorm operator
- Create a Top-K selection kernel
- Build a 2D convolution operator using im2col

**Troubleshooting**
- Validate this TileLang operator code
- I'm getting a compilation error with WGMMA on A100 — help me fix it
- Why is my kernel producing incorrect results on AMD?

**Guided Workflow**
- Walk me through developing a GEMM kernel step by step
- Help me adapt my H100 kernel to work on A100

## MCP Tools

The MCP server provides 13 tools:

| Tool | Description |
|------|-------------|
| `inspect_tilelang_workspace` | Validate TileLang repository and knowledge base |
| `validate_knowledge_base` | Parse and validate JSON/JSONL delivery files |
| `normalize_device_profile` | Normalize vendor/model/target to canonical form |
| `search_capabilities` | Search capability map for operator categories |
| `search_patterns` | Search for reusable operator implementation patterns |
| `search_usage_patterns` | Search for example workflows and call sequences |
| `lookup_apis` | Search for TileLang API symbols and signatures |
| `get_source_chunks` | Retrieve focused source code reference chunks |
| `trace_semantic_graph` | Trace concept/symbol/pattern dependency graph |
| `build_operator_retrieval_plan` | Assemble a structured retrieval plan for an operator |
| `search_troubleshooting` | Search troubleshooting knowledge base for solutions |
| `validate_operator_code` | Static analysis of generated TileLang code |
| `operator_development_wizard` | 12-step guided development workflow |

## Standard Workflow

The skill follows a strict retrieval-before-generation workflow:

1. **Validate Workspace** — Confirm TileLang source and knowledge base
2. **Normalize Device** — Resolve vendor/model/target
3. **Search Capabilities** — Identify operator category
4. **Search Patterns** — Find reusable implementation patterns
5. **Search Usage Patterns** — Find example workflows
6. **Confirm APIs** — Verify required symbols and signatures
7. **Source Fallback** — Retrieve source chunks if needed
8. **Build Retrieval Plan** — Synthesize all findings
9. **Generate Code** — The only step that produces code
10. **Validate Code** — Static analysis and checks

## Device Support

| Device | Target | Confidence |
|--------|--------|------------|
| NVIDIA A100 | `cuda -arch=sm_80` | High |
| NVIDIA H100 | `cuda -arch=sm_90` | High |
| NVIDIA B100 | `cuda -arch=sm_100a` | Medium |
| AMD MI300X | `hip -mcpu=gfx940` | Medium |
| AMD MI350 | `hip -mcpu=gfx950` | Medium |
| CPU | `llvm` / `c` | High |
| Apple Silicon | `metal` | Medium |
| WebGPU | `webgpu` | Low |

## Development

```bash
# Self-check
python scripts/tilelang_operator_mcp.py --check

# Smoke test (all 13 tools)
python .claude/skills/run-tilelang-mcp/driver.py --smoke

# Call a single tool
python .claude/skills/run-tilelang-mcp/driver.py --call normalize_device_profile \
  --args '{"vendor":"nvidia","model":"H100","target":"cuda"}'

# Run tests
python -m pytest tests/test_mcp_server.py -v
```

## Documentation

| Document | Description |
|----------|-------------|
| [SKILL.md](SKILL.md) | Core skill instructions for AI agents |
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | Detailed setup guide |
| [CHANGELOG.md](CHANGELOG.md) | Version history |
| [examples/](examples/) | Usage examples |
| [tests/](tests/) | Test cases |

## License

Apache-2.0

---

## 中文

**[English](#tilelang-operator-dev)** | **中文**

基于 MCP 的 TileLang 算子开发 Claude Code 技能，提供 13 个工具用于工作区验证、知识检索、设备感知规划和代码验证。

### 特性

- **智能自动检测** — 自动定位 TileLang 源码仓库（零配置）
- **双工作区模式** — 算子开发目录独立于 TileLang 源码
- **内置知识库** — 预生成的模式、API、使用工作流和源码片段
- **设备感知规划** — 支持 NVIDIA、AMD、CPU、Apple Silicon 和 WebGPU
- **验证优先工作流** — 生成代码前强制进行工作区和知识库验证
- **开发向导** — 从意图到验证代码的 12 步引导式工作流

### 前置条件

- Python 3.8+
- Claude Code
- TileLang 源码仓库（克隆或 pip 安装）

技能会在生成代码前验证工作区。没有有效的 TileLang 工作区时会停止并拒绝继续。

### 安装

#### 快速开始

```bash
# 克隆
git clone https://github.com/Leafoon/tilelang-operator-dev.git
git clone https://github.com/tile-ai/tilelang.git

# 全局安装 skill 和 MCP 配置
cd tilelang-operator-dev && bash setup.sh && cd ..

# 创建算子工作区
mkdir my-operators

# 重启 Claude Code，然后：
cd my-operators && claude .
```

`setup.sh` 脚本安装：
- Skill 到 `~/.claude/skills/run-tilelang-mcp/`
- MCP 配置到 `~/.claude/.mcp.json`

重启后 Claude Code 从任意目录均可发现该技能。

#### 手动安装

```bash
# Skill
mkdir -p ~/.claude/skills/run-tilelang-mcp
cp tilelang-operator-dev/.claude/skills/run-tilelang-mcp/SKILL.md ~/.claude/skills/run-tilelang-mcp/

# MCP 配置（编辑脚本路径）
cat > ~/.claude/.mcp.json << 'EOF'
{
  "mcpServers": {
    "tilelang-operator-knowledge": {
      "command": "python3",
      "args": ["/path/to/tilelang-operator-dev/scripts/tilelang_operator_mcp.py"]
    }
  }
}
EOF
```

#### Windows

MCP 服务器默认使用 `python3`。Windows 上请改为 `python`：

```json
{
  "mcpServers": {
    "tilelang-operator-knowledge": {
      "command": "python",
      "args": ["C:\\path\\to\\tilelang-operator-dev\\scripts\\tilelang_operator_mcp.py"]
    }
  }
}
```

### 使用方法

在算子目录中打开 Claude Code，直接提问即可。技能会在检测到 TileLang 算子开发请求时自动调用。

### 使用示例

**GEMM 算子**
- 写一个 NVIDIA H100 的基础 GEMM 算子，fp16 输入
- 开发一个 split-K GEMM 算子，用于大 K 维度
- 为 A100 创建 2:4 稀疏 GEMM 算子
- 构建一个 MoE 风格的分组 GEMM 算子

**Attention 算子**
- 实现一个 H100 的 flash attention 前向算子
- 写一个带分页 KV 缓存的 GQA decode attention 算子
- 为 DeepSeek 模型创建 MLA decode 算子

**设备适配**
- 写一个能在 Apple M4 上运行的 GEMM 算子，使用 Metal 后端
- 为 AMD MI300X 创建 elementwise add 算子
- 为 NVIDIA B100 Blackwell 架构开发 GEMM 算子

**归约与其他**
- 实现一个 online softmax 算子
- 写一个 RMSNorm 算子
- 创建一个 Top-K 选择算子
- 用 im2col 构建 2D 卷积算子

**故障排查**
- 验证这段 TileLang 算子代码
- 我的 WGMMA 在 A100 上编译报错，帮我修复
- 为什么我的 AMD 算子输出结果不正确？

**引导式开发**
- 一步步指导我开发一个 GEMM 算子
- 帮我把 H100 的算子适配到 A100

### MCP 工具

MCP 服务器提供 13 个工具：

| 工具 | 描述 |
|------|------|
| `inspect_tilelang_workspace` | 验证 TileLang 仓库和知识库 |
| `validate_knowledge_base` | 解析和验证 JSON/JSONL 交付文件 |
| `normalize_device_profile` | 将供应商/型号/目标标准化为规范形式 |
| `search_capabilities` | 搜索能力图谱查找算子类别 |
| `search_patterns` | 搜索可复用的算子实现模式 |
| `search_usage_patterns` | 搜索示例工作流和调用序列 |
| `lookup_apis` | 搜索 TileLang API 符号和签名 |
| `get_source_chunks` | 获取聚焦的源码参考片段 |
| `trace_semantic_graph` | 追踪概念/符号/模式依赖图 |
| `build_operator_retrieval_plan` | 为算子构建结构化检索计划 |
| `search_troubleshooting` | 搜索故障排查知识库获取解决方案 |
| `validate_operator_code` | 对生成的 TileLang 代码进行静态分析 |
| `operator_development_wizard` | 12 步引导式开发工作流 |

### 标准工作流

技能遵循严格的「先检索后生成」工作流：

1. **验证工作区** — 确认 TileLang 源码和知识库
2. **标准化设备** — 解析供应商/型号/目标
3. **搜索能力** — 识别算子类别
4. **搜索模式** — 查找可复用的实现模式
5. **搜索使用模式** — 查找示例工作流
6. **确认 API** — 验证所需符号和签名
7. **源码回退** — 需要时获取源码片段
8. **构建检索计划** — 综合所有发现
9. **生成代码** — 唯一产生代码的步骤
10. **验证代码** — 静态分析和检查

### 设备支持

| 设备 | 目标 | 置信度 |
|------|------|--------|
| NVIDIA A100 | `cuda -arch=sm_80` | 高 |
| NVIDIA H100 | `cuda -arch=sm_90` | 高 |
| NVIDIA B100 | `cuda -arch=sm_100a` | 中 |
| AMD MI300X | `hip -mcpu=gfx940` | 中 |
| AMD MI350 | `hip -mcpu=gfx950` | 中 |
| CPU | `llvm` / `c` | 高 |
| Apple Silicon | `metal` | 中 |
| WebGPU | `webgpu` | 低 |

### 开发

```bash
# 自检
python scripts/tilelang_operator_mcp.py --check

# 冒烟测试（全部 13 个工具）
python .claude/skills/run-tilelang-mcp/driver.py --smoke

# 调用单个工具
python .claude/skills/run-tilelang-mcp/driver.py --call normalize_device_profile \
  --args '{"vendor":"nvidia","model":"H100","target":"cuda"}'

# 运行测试
python -m pytest tests/test_mcp_server.py -v
```

### 文档

| 文档 | 描述 |
|------|------|
| [SKILL.md](SKILL.md) | AI 代理的核心技能指令 |
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | 详细设置指南 |
| [CHANGELOG.md](CHANGELOG.md) | 版本历史 |
| [examples/](examples/) | 使用示例 |
| [tests/](tests/) | 测试用例 |

### 许可证

Apache-2.0
