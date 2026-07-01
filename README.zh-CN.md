# TileLang Operator Dev

[English](README.md) | [简体中文](README.zh-CN.md)

TileLang Operator Dev 是面向 Claude Code 的 TileLang 算子开发 Skill 与 MCP 服务。它用于在独立算子工作区中完成工作区验证、TileLang 知识检索、设备目标规范化、实现规划、代码校验和故障排查，并要求在生成代码前先完成验证和检索。

## 能力概览

- **Claude Code Skill**：`tilelang-operator-dev`，用于 TileLang 算子的设计、实现、迁移、验证和解释。
- **MCP 服务**：`tilelang-operator-knowledge`，提供 13 个工具，用于工作区验证、知识检索、开发规划、故障排查和静态代码检查。
- **独立算子工作区**：自定义算子可以放在 TileLang 源码仓库之外。
- **内置知识库**：默认使用 `resources/tilelang_knowledge/`，也支持工作区本地覆盖。
- **设备感知流程**：在选择特定硬件实现模式前，先规范化 NVIDIA、AMD、CPU、Apple Silicon 和 WebGPU 目标。

## 推荐目录结构

推荐把三个目录放在同一个本地父目录下。这个父目录可以是用户机器上的任意位置，例如项目目录、临时实验目录或共享工作区。

```text
<workspace-root>/
├── tilelang-operator-dev/      # 本仓库：Skill、MCP 服务、内置知识库
├── tilelang/                   # TileLang 官方源码仓库
└── my-operators/               # 独立 Claude Code 算子工作区
```

从算子工作区启动 Claude Code：

```bash
cd <workspace-root>/my-operators
claude .
```

`my-operators` 中不应该嵌套完整的 `tilelang-operator-dev` 仓库。如果使用工作区本地 Skill 发现，`my-operators/.claude/skills/tilelang-operator-dev/SKILL.md` 只是一个轻量 Claude Code 入口文件。

## 前置条件

- Python 3.8+
- Claude Code
- TileLang 官方源码仓库的本地 checkout

示例配置：

```bash
mkdir -p <workspace-root>
cd <workspace-root>
git clone https://github.com/Leafoon/tilelang-operator-dev.git
git clone https://github.com/tile-ai/tilelang.git
```

请将 `<workspace-root>` 替换为你实际使用的任意本地目录。

## 配置模式

### 方案 A：Claude Code 全局配置

如果希望 Claude Code 在任意算子工作区都能发现该 Skill 和 MCP 服务，使用全局配置。

```bash
cd <workspace-root>/tilelang-operator-dev
bash setup.sh
```

该脚本会安装：

- Skill：`~/.claude/skills/tilelang-operator-dev/SKILL.md`
- MCP 配置：`~/.claude/.mcp.json`
- MCP 服务目标：`<workspace-root>/tilelang-operator-dev/scripts/tilelang_operator_mcp.py`

生成的 MCP 配置形态如下：

```json
{
  "mcpServers": {
    "tilelang-operator-knowledge": {
      "command": "python3",
      "args": ["<workspace-root>/tilelang-operator-dev/scripts/tilelang_operator_mcp.py"]
    }
  }
}
```

完成配置后重启 Claude Code，然后打开算子工作区：

```bash
mkdir -p <workspace-root>/my-operators
cd <workspace-root>/my-operators
claude .
```

### 方案 B：工作区本地配置

如果希望算子工作区自带 `.mcp.json` 和轻量 Skill 入口，使用工作区本地配置。

```bash
cd <workspace-root>
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

这个相对路径假设 `my-operators` 和 `tilelang-operator-dev` 是同级目录。如果你的目录结构不同，请改成绝对路径。

## 源码和知识库解析规则

MCP 服务按以下顺序解析 TileLang 源码仓库：

1. 工具参数中的 `tilelang_source_path`
2. 环境变量 `TILELANG_SOURCE_PATH`
3. 自动发现的同级或父级 `tilelang/` 目录
4. 当前工作区，作为向后兼容的最后回退

知识库按以下顺序解析：

1. 工作区本地 `tilelang_knowledge/`，如果存在且足够完整
2. 本仓库内置的 `resources/tilelang_knowledge/`

这样可以让算子工作区保持小而专注，只存放自定义算子。

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

- "Develop a basic fp16 GEMM operator for NVIDIA H100 in TileLang."
- "Adapt this H100 TileLang kernel for A100 and explain the required scheduling changes."
- "Validate this TileLang operator and identify likely correctness or performance issues."
- "Walk me through a grouped GEMM operator for MoE-style workloads."

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

在 `tilelang-operator-dev` 仓库中运行：

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
<workspace-root>/my-operators/.claude/skills/tilelang-operator-dev/SKILL.md
```

### MCP 服务不可用

检查 `.mcp.json`，确认脚本路径指向克隆的 `tilelang-operator-dev` 仓库：

```text
<workspace-root>/tilelang-operator-dev/scripts/tilelang_operator_mcp.py
```

然后运行：

```bash
python <workspace-root>/tilelang-operator-dev/scripts/tilelang_operator_mcp.py --check
```

### 找不到 TileLang 源码仓库

使用以下任一修复方式：

- 将官方仓库放在 `<workspace-root>/tilelang`。
- 在 MCP 配置中设置 `TILELANG_SOURCE_PATH`。
- 调用 MCP 工具时传入 `tilelang_source_path`。

### 知识库验证失败

内置知识库应位于：

```text
<workspace-root>/tilelang-operator-dev/resources/tilelang_knowledge/
```

只有在需要自定义覆盖时，才建议在算子工作区添加本地 `tilelang_knowledge/`。

## 许可证

Apache-2.0
