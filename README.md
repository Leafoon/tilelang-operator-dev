# TileLang Operator Dev

**English** | [中文](#中文)

A Claude Code skill and MCP server for TileLang operator development. It supports independent operator workspaces, MCP-backed knowledge retrieval, device-aware planning, code validation, and troubleshooting.

## What This Provides

- **Claude Code skill**: `tilelang-operator-dev`, used for TileLang operator design, implementation, adaptation, validation, and explanation.
- **MCP server**: `tilelang-operator-knowledge`, with 13 tools for workspace validation, retrieval, planning, troubleshooting, and static code checks.
- **Dual-workspace support**: keep custom operators outside the TileLang source tree.
- **Bundled knowledge base**: use `resources/tilelang_knowledge/` by default, with optional workspace-local overrides.
- **Device-aware workflow**: normalize NVIDIA, AMD, CPU, Apple Silicon, and WebGPU targets before selecting target-specific patterns.

## Recommended Layout

The recommended local layout keeps the skill repository, the official TileLang repository, and the operator workspace as siblings:

```text
/temp/
├── tilelang-operator-dev/      # this repository: skill, MCP server, bundled knowledge
├── tilelang/                   # official TileLang source repository
└── my-operators/               # independent Claude Code operator workspace
```

In this layout, open Claude Code from `/temp/my-operators`:

```bash
cd /temp/my-operators
claude .
```

The workspace should not contain a full nested copy of `tilelang-operator-dev`. If workspace-local skill discovery is used, `my-operators/.claude/skills/tilelang-operator-dev/SKILL.md` is only a lightweight Claude Code entrypoint.

## Prerequisites

- Python 3.8+
- Claude Code
- A TileLang source checkout, usually:

```bash
cd /temp
git clone https://github.com/Leafoon/tilelang-operator-dev.git
git clone https://github.com/tile-ai/tilelang.git
```

## Configuration Modes

### Option A: Global Configuration

Use global configuration when you want Claude Code to discover the skill and MCP server from any workspace.

```bash
cd /temp/tilelang-operator-dev
bash setup.sh
```

This installs:

- Skill: `~/.claude/skills/tilelang-operator-dev/SKILL.md`
- MCP config: `~/.claude/.mcp.json`
- MCP server target: `/temp/tilelang-operator-dev/scripts/tilelang_operator_mcp.py`

The generated MCP config has this shape:

```json
{
  "mcpServers": {
    "tilelang-operator-knowledge": {
      "command": "python3",
      "args": ["/temp/tilelang-operator-dev/scripts/tilelang_operator_mcp.py"]
    }
  }
}
```

After setup, restart Claude Code, then open any operator workspace:

```bash
mkdir -p /temp/my-operators
cd /temp/my-operators
claude .
```

### Option B: Workspace Configuration

Use workspace configuration when you want a portable operator workspace that carries its own `.mcp.json` and lightweight skill entrypoint.

```bash
cd /temp
cp -R tilelang-operator-dev/resources/operator_template my-operators
cd my-operators
claude .
```

The template includes:

- `.mcp.json`, pointing to `../tilelang-operator-dev/scripts/tilelang_operator_mcp.py`
- `.claude/skills/tilelang-operator-dev/SKILL.md`, a lightweight Claude Code skill entrypoint
- `init_operator.py`, for creating operator directories
- `example_operator/`, a starter operator layout

Default workspace MCP config:

```json
{
  "mcpServers": {
    "tilelang-operator-knowledge": {
      "command": "python3",
      "args": [
        "${workspaceFolder}/../tilelang-operator-dev/scripts/tilelang_operator_mcp.py"
      ]
    }
  }
}
```

If your TileLang source checkout is not a sibling directory named `tilelang`, set `TILELANG_SOURCE_PATH` in the MCP config or pass `tilelang_source_path` to MCP tools.

## How Source And Knowledge Are Resolved

The MCP server resolves the TileLang source repository in this order:

1. Explicit `tilelang_source_path` tool argument
2. `TILELANG_SOURCE_PATH` environment variable
3. Auto-detected sibling or parent `tilelang/` directory
4. Active workspace as a backward-compatible fallback

The knowledge base resolves in this order:

1. Workspace-local `tilelang_knowledge/`, if present and complete enough
2. Bundled `resources/tilelang_knowledge/` from this repository

This means `/temp/my-operators` can stay small and focused on custom operators.

## Standard Claude Code Workflow

Ask Claude Code for TileLang operator work from the operator workspace. The skill should validate and retrieve before writing code:

1. Validate workspace: `inspect_tilelang_workspace`
2. Validate knowledge base: `validate_knowledge_base`
3. Normalize device: `normalize_device_profile`
4. Search capabilities, patterns, usage records, APIs, and source chunks
5. Build a retrieval plan
6. Generate code or explanation
7. Validate generated code
8. Troubleshoot compile/runtime/performance issues if needed

Example prompts:

- "Develop a basic fp16 GEMM operator for NVIDIA H100 in TileLang."
- "Adapt this H100 TileLang kernel for A100 and explain the required scheduling changes."
- "Validate this TileLang operator and identify likely correctness or performance issues."
- "Walk me through a grouped GEMM operator for MoE-style workloads."

## MCP Tools

| Tool | Purpose |
|------|---------|
| `inspect_tilelang_workspace` | Validate operator workspace, TileLang source, and knowledge availability |
| `validate_knowledge_base` | Validate required delivery files and parse JSON/JSONL records |
| `normalize_device_profile` | Normalize vendor/model/target information |
| `search_capabilities` | Find matching operator capability categories |
| `search_patterns` | Retrieve reusable implementation patterns |
| `search_usage_patterns` | Retrieve compile, run, compare, and profile workflows |
| `lookup_apis` | Confirm TileLang API signatures, modules, and visibility |
| `get_source_chunks` | Retrieve focused source fallback chunks |
| `trace_semantic_graph` | Trace concepts, symbols, and pattern dependencies |
| `build_operator_retrieval_plan` | Assemble a structured operator retrieval plan |
| `search_troubleshooting` | Search known error patterns and fixes |
| `validate_operator_code` | Run static checks on generated TileLang code |
| `operator_development_wizard` | Guide a step-by-step operator development workflow |

## Device Support

| Device family | Typical target | Confidence |
|---------------|----------------|------------|
| NVIDIA A100 / Ampere | `cuda -arch=sm_80` | High when confirmed by user or source evidence |
| NVIDIA H100 / Hopper | `cuda -arch=sm_90` | High when confirmed by user or source evidence |
| NVIDIA B100 / Blackwell | `cuda -arch=sm_100a` | Medium until current repo support is verified |
| AMD MI300X / MI350 | `hip -mcpu=gfx940` / `gfx950` | Medium when exact gfx arch is known |
| CPU | `llvm` or `c` | High for supported CPU paths |
| Apple Silicon | `metal` | Medium, verify repository support |
| WebGPU | `webgpu` | Low to medium, verify repository support |

Architecture-specific features such as WGMMA, TCGEN05, TMA, `cp.async`, MFMA, LDS, TMEM, `cluster_dims`, and `is_cpu=True` must be verified against retrieved knowledge and source/API evidence before they are recommended.

## Validation

From `/temp/tilelang-operator-dev`:

```bash
python -m pytest tests/test_mcp_server.py -q
python scripts/tilelang_operator_mcp.py --check
python .claude/skills/run-tilelang-mcp/driver.py --smoke
```

The `run-tilelang-mcp` skill and driver are retained for MCP server development and smoke testing. They are not the default user-facing operator development skill.

## Troubleshooting

### Claude Code does not trigger the operator skill

Confirm the installed or workspace-local skill path:

```text
~/.claude/skills/tilelang-operator-dev/SKILL.md
```

or:

```text
/temp/my-operators/.claude/skills/tilelang-operator-dev/SKILL.md
```

### MCP server is not available

Check `.mcp.json` and verify that the script path points to the cloned `tilelang-operator-dev` repository:

```text
/temp/tilelang-operator-dev/scripts/tilelang_operator_mcp.py
```

Then run:

```bash
python /temp/tilelang-operator-dev/scripts/tilelang_operator_mcp.py --check
```

### TileLang source is not found

Use one of these fixes:

- Place the official repository at `/temp/tilelang`.
- Set `TILELANG_SOURCE_PATH` in the MCP config.
- Pass `tilelang_source_path` when calling MCP tools.

### Knowledge base validation fails

The bundled knowledge base should be present at:

```text
/temp/tilelang-operator-dev/resources/tilelang_knowledge/
```

Only add workspace-local `tilelang_knowledge/` if you need custom overrides.

## License

Apache-2.0

---

## 中文

**[English](#tilelang-operator-dev)** | **中文**

TileLang Operator Dev 是面向 Claude Code 的 TileLang 算子开发 Skill 与 MCP 服务。它支持独立算子工作区、基于 MCP 的知识检索、设备感知规划、代码校验与故障排查。

## 能力概览

- **Claude Code Skill**：`tilelang-operator-dev`，用于 TileLang 算子的设计、实现、迁移、验证和解释。
- **MCP 服务**：`tilelang-operator-knowledge`，提供 13 个工具，用于工作区验证、知识检索、开发规划、故障排查和静态代码检查。
- **双工作区支持**：自定义算子可以放在 TileLang 源码仓库之外。
- **内置知识库**：默认使用 `resources/tilelang_knowledge/`，也支持工作区本地覆盖。
- **设备感知流程**：在选择特定硬件模式前，先规范化 NVIDIA、AMD、CPU、Apple Silicon 和 WebGPU 目标。

## 推荐目录结构

推荐把 Skill 仓库、TileLang 官方仓库和算子工作区放在同一级目录：

```text
/temp/
├── tilelang-operator-dev/      # 本仓库：Skill、MCP 服务、内置知识库
├── tilelang/                   # TileLang 官方源码仓库
└── my-operators/               # 独立 Claude Code 算子工作区
```

在这个布局下，从 `/temp/my-operators` 启动 Claude Code：

```bash
cd /temp/my-operators
claude .
```

`my-operators` 中不应该嵌套完整的 `tilelang-operator-dev` 仓库。如果使用工作区本地 Skill 发现，`my-operators/.claude/skills/tilelang-operator-dev/SKILL.md` 只是一个轻量 Claude Code 入口文件。

## 前置条件

- Python 3.8+
- Claude Code
- TileLang 源码仓库，通常按以下方式准备：

```bash
cd /temp
git clone https://github.com/Leafoon/tilelang-operator-dev.git
git clone https://github.com/tile-ai/tilelang.git
```

## 配置模式

### 方案 A：全局配置

如果希望 Claude Code 在任意工作区都能发现该 Skill 和 MCP 服务，使用全局配置。

```bash
cd /temp/tilelang-operator-dev
bash setup.sh
```

该脚本会安装：

- Skill：`~/.claude/skills/tilelang-operator-dev/SKILL.md`
- MCP 配置：`~/.claude/.mcp.json`
- MCP 服务目标：`/temp/tilelang-operator-dev/scripts/tilelang_operator_mcp.py`

生成的 MCP 配置形态如下：

```json
{
  "mcpServers": {
    "tilelang-operator-knowledge": {
      "command": "python3",
      "args": ["/temp/tilelang-operator-dev/scripts/tilelang_operator_mcp.py"]
    }
  }
}
```

完成配置后重启 Claude Code，然后打开任意算子工作区：

```bash
mkdir -p /temp/my-operators
cd /temp/my-operators
claude .
```

### 方案 B：工作区配置

如果希望一个算子工作区自带 `.mcp.json` 和轻量 Skill 入口，使用工作区配置。

```bash
cd /temp
cp -R tilelang-operator-dev/resources/operator_template my-operators
cd my-operators
claude .
```

模板包含：

- `.mcp.json`，指向 `../tilelang-operator-dev/scripts/tilelang_operator_mcp.py`
- `.claude/skills/tilelang-operator-dev/SKILL.md`，轻量 Claude Code Skill 入口
- `init_operator.py`，用于创建算子目录
- `example_operator/`，算子起始模板

默认工作区 MCP 配置：

```json
{
  "mcpServers": {
    "tilelang-operator-knowledge": {
      "command": "python3",
      "args": [
        "${workspaceFolder}/../tilelang-operator-dev/scripts/tilelang_operator_mcp.py"
      ]
    }
  }
}
```

如果 TileLang 源码仓库不是名为 `tilelang` 的同级目录，可以在 MCP 配置中设置 `TILELANG_SOURCE_PATH`，或在调用 MCP 工具时传入 `tilelang_source_path`。

## 源码和知识库解析规则

MCP 服务按以下顺序解析 TileLang 源码仓库：

1. 工具参数中的 `tilelang_source_path`
2. 环境变量 `TILELANG_SOURCE_PATH`
3. 自动发现的同级或父级 `tilelang/` 目录
4. 当前工作区，作为向后兼容的最后回退

知识库按以下顺序解析：

1. 工作区本地 `tilelang_knowledge/`，如果存在且足够完整
2. 本仓库内置的 `resources/tilelang_knowledge/`

因此，`/temp/my-operators` 可以保持小而专注，只存放自定义算子。

## Claude Code 标准流程

在算子工作区中向 Claude Code 提出 TileLang 算子需求。Skill 应该先验证和检索，再生成代码：

1. 验证工作区：`inspect_tilelang_workspace`
2. 验证知识库：`validate_knowledge_base`
3. 规范化设备：`normalize_device_profile`
4. 检索 capability、pattern、usage、API 和源码片段
5. 构建检索计划
6. 生成代码或解释
7. 验证生成的代码
8. 必要时排查编译、运行或性能问题

示例提示：

- “Develop a basic fp16 GEMM operator for NVIDIA H100 in TileLang.”
- “Adapt this H100 TileLang kernel for A100 and explain the required scheduling changes.”
- “Validate this TileLang operator and identify likely correctness or performance issues.”
- “Walk me through a grouped GEMM operator for MoE-style workloads.”

## MCP 工具

| 工具 | 用途 |
|------|------|
| `inspect_tilelang_workspace` | 验证算子工作区、TileLang 源码和知识库可用性 |
| `validate_knowledge_base` | 验证交付文件并解析 JSON/JSONL 记录 |
| `normalize_device_profile` | 规范化厂商、型号和目标后端 |
| `search_capabilities` | 查找匹配的算子能力类别 |
| `search_patterns` | 检索可复用实现模式 |
| `search_usage_patterns` | 检索编译、运行、比对和性能测试流程 |
| `lookup_apis` | 确认 TileLang API 签名、模块和可见性 |
| `get_source_chunks` | 获取聚焦的源码回退片段 |
| `trace_semantic_graph` | 追踪概念、符号和模式依赖 |
| `build_operator_retrieval_plan` | 生成结构化算子检索计划 |
| `search_troubleshooting` | 搜索已知错误模式和修复建议 |
| `validate_operator_code` | 对生成的 TileLang 代码做静态检查 |
| `operator_development_wizard` | 提供分步骤算子开发向导 |

## 设备支持

| 设备类别 | 典型目标 | 置信度 |
|----------|----------|--------|
| NVIDIA A100 / Ampere | `cuda -arch=sm_80` | 用户或源码证据确认后为高 |
| NVIDIA H100 / Hopper | `cuda -arch=sm_90` | 用户或源码证据确认后为高 |
| NVIDIA B100 / Blackwell | `cuda -arch=sm_100a` | 需验证当前仓库支持，默认中等 |
| AMD MI300X / MI350 | `hip -mcpu=gfx940` / `gfx950` | 已知精确 gfx 架构时为中等 |
| CPU | `llvm` 或 `c` | 支持路径明确时为高 |
| Apple Silicon | `metal` | 需验证仓库支持，默认中等 |
| WebGPU | `webgpu` | 需验证仓库支持，低到中等 |

WGMMA、TCGEN05、TMA、`cp.async`、MFMA、LDS、TMEM、`cluster_dims` 和 `is_cpu=True` 等架构相关特性，必须先通过检索到的知识记录和源码/API 证据确认，再进行推荐。

## 验证

在 `/temp/tilelang-operator-dev` 中运行：

```bash
python -m pytest tests/test_mcp_server.py -q
python scripts/tilelang_operator_mcp.py --check
python .claude/skills/run-tilelang-mcp/driver.py --smoke
```

`run-tilelang-mcp` Skill 和 driver 保留用于 MCP 服务开发与 smoke test。它不是默认面向用户的算子开发 Skill。

## 常见问题

### Claude Code 没有触发算子开发 Skill

确认已安装或工作区本地存在以下 Skill 路径：

```text
~/.claude/skills/tilelang-operator-dev/SKILL.md
```

或：

```text
/temp/my-operators/.claude/skills/tilelang-operator-dev/SKILL.md
```

### MCP 服务不可用

检查 `.mcp.json`，确认脚本路径指向克隆的 `tilelang-operator-dev` 仓库：

```text
/temp/tilelang-operator-dev/scripts/tilelang_operator_mcp.py
```

然后运行：

```bash
python /temp/tilelang-operator-dev/scripts/tilelang_operator_mcp.py --check
```

### 找不到 TileLang 源码仓库

使用以下任一修复方式：

- 将官方仓库放在 `/temp/tilelang`。
- 在 MCP 配置中设置 `TILELANG_SOURCE_PATH`。
- 调用 MCP 工具时传入 `tilelang_source_path`。

### 知识库验证失败

内置知识库应位于：

```text
/temp/tilelang-operator-dev/resources/tilelang_knowledge/
```

只有在需要自定义覆盖时，才建议在算子工作区添加本地 `tilelang_knowledge/`。

## 许可证

Apache-2.0
