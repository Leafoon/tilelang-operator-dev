# TileLang Operator Dev

[English](README.md) | [简体中文](README.zh-CN.md)

TileLang Operator Dev 是面向 Claude Code 的 TileLang 算子开发 Skill 与 MCP 服务。它用于在独立算子工作区中完成工作区验证、TileLang 知识检索、设备目标规范化、实现规划、代码校验和故障排查，并要求在生成代码前先完成验证和检索。

## 能力概览

- **Claude Code Skill**：`tilelang-operator-dev`，用于 TileLang 算子的设计、实现、迁移、验证和解释。
- **MCP 服务**：`tilelang-operator-knowledge`，提供 13 个工具，用于工作区验证、知识检索、开发规划、故障排查和静态代码检查。
- **独立算子工作区**：自定义算子可以放在 TileLang 源码仓库之外。
- **内置知识库**：默认使用 `resources/tilelang_knowledge/`，也支持工作区本地覆盖。
- **设备感知流程**：在选择特定硬件实现模式前，先规范化 NVIDIA、AMD、CPU、Apple Silicon 和 WebGPU 目标；其他加速器厂商在缺少后端证据时只标记为受限。

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

- Python 3.10+
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

## 快速开始

最推荐的起步方式是全局配置模式：完整 Skill 和 MCP 服务保留在 `tilelang-operator-dev` 仓库中，自定义算子放在独立工作区。

```bash
mkdir -p <workspace-root>
cd <workspace-root>

git clone https://github.com/Leafoon/tilelang-operator-dev.git
git clone https://github.com/tile-ai/tilelang.git
mkdir -p my-operators

cd tilelang-operator-dev
bash setup.sh

cd ../my-operators
claude .
```

如果默认 `python3` 低于 3.10，请显式指定 Python：

```bash
cd <workspace-root>/tilelang-operator-dev
PYTHON=/path/to/python3.10 bash setup.sh
```

进入 Claude Code 后，可以从这样的问题开始：

```text
Use the tilelang-operator-dev skill. Inspect this workspace, confirm TileLang source and knowledge availability, then create a retrieval plan for an fp16 GEMM operator on NVIDIA H100.
```

## 配置模式

### 方案 A：Claude Code 全局配置

如果希望 Claude Code 在任意算子工作区都能发现该 Skill 和 MCP 服务，使用全局配置。

```bash
cd <workspace-root>/tilelang-operator-dev
bash setup.sh
```

如果希望 Claude Code 使用指定 Python 启动 MCP 服务，可以运行 `PYTHON=/path/to/python3.10 bash setup.sh`。

该脚本会安装或更新：

- Skill：`~/.claude/skills/tilelang-operator-dev/SKILL.md`
- MCP 配置：`~/.claude/.mcp.json`
- MCP 服务目标：`<workspace-root>/tilelang-operator-dev/scripts/tilelang_operator_mcp.py`

如果 `~/.claude/.mcp.json` 已存在，`setup.sh` 会保留已有 MCP server，只更新 `tilelang-operator-knowledge`，并在写入前创建带时间戳的备份。

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

从模板创建新的算子目录：

```bash
python init_operator.py --new-operator fused_moe_gemm
```

模板包含：

- `.mcp.json`，指向 `../tilelang-operator-dev/scripts/tilelang_operator_mcp.py`
- `.claude/skills/tilelang-operator-dev/SKILL.md`，轻量 Claude Code Skill 入口
- `init_operator.py`，用于创建算子目录，并校验附近、显式指定或 `TILELANG_SOURCE_PATH` 指向的 TileLang 源码仓库
- `example_operator/`，算子起始模板

模板不包含 `tilelang_knowledge/`。Claude Code 通常使用 `tilelang-operator-dev` 内置知识库；只有需要完整自定义覆盖时，才创建工作区本地 `tilelang_knowledge/`。

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

如果 TileLang 官方仓库不在同级 `tilelang/` 目录下，可以在 MCP 配置中设置 `TILELANG_SOURCE_PATH`，或在调试 MCP 工具时显式传入 `tilelang_source_path`。日常 Claude Code 使用中，同级 `tilelang/` 或环境变量是最不容易产生歧义的配置方式。

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

## 在 Claude Code 中使用

请从算子工作区启动 Claude Code，而不是从 `tilelang-operator-dev` 仓库启动：

```bash
cd <workspace-root>/my-operators
claude .
```

在 Claude Code 里，通常不需要手动调用 MCP 工具。你只需要用自然语言描述算子任务；如果希望明确触发该 Skill，可以在问题开头写 `Use the tilelang-operator-dev skill`。Skill 应该先验证和检索，再生成代码：

1. 验证工作区：`inspect_tilelang_workspace`
2. 验证知识库：`validate_knowledge_base`
3. 规范化设备：`normalize_device_profile`
4. 检索 capability、pattern、usage、API 和源码片段
5. 构建检索计划
6. 生成代码或解释
7. 验证生成的代码
8. 必要时排查编译、运行或性能问题

Claude Code 的第一轮有效回答应该先给出 retrieval trace，包括算子工作区、TileLang 源码路径、知识库路径、设备 profile、选中的 capability/pattern/usage 记录、API 符号、源码 fallback 片段、风险和置信度。

### 推荐问题结构

实现类问题建议这样写：

```text
Use the tilelang-operator-dev skill.

Task:
- Build / adapt / explain / validate a TileLang operator.

Operator:
- Type: GEMM / grouped GEMM / attention / reduction / custom
- Shapes: M=?, N=?, K=?, batch=?, heads=?, block sizes if known
- Dtypes: input=?, accumulator=?, output=?
- Layout: row-major / column-major / transposed / packed / sparse

Hardware:
- Vendor and model: NVIDIA H100 / A100 / AMD MI300X / CPU / ...
- Target if known: cuda -arch=sm_90 / hip -mcpu=gfx942 / llvm / ...
- Required features: WGMMA / TMA / cp.async / MFMA / none / unknown

Constraints:
- Correctness tolerance:
- Performance goal:
- Memory limit:
- Must reuse or avoid:

Existing material:
- Paste current code, error logs, benchmark output, or say "from scratch".

Expected output:
- Retrieval trace first, then implementation plan, code, tests, and validation steps.
```

排障类问题建议这样写：

```text
Use the tilelang-operator-dev skill to debug this TileLang issue.

Environment:
- TileLang source path:
- Python version:
- GPU/CPU model and target:

Command I ran:
<paste command>

Error:
<paste full error log>

Code:
<paste relevant operator code>

Expected:
<what should have happened>
```

### 示例提示

- "Develop a basic fp16 GEMM operator for NVIDIA H100 in TileLang."
- "Adapt this H100 TileLang kernel for A100 and explain the required scheduling changes."
- "Validate this TileLang operator and identify likely correctness or performance issues."
- "Walk me through a grouped GEMM operator for MoE-style workloads."
- "Use tilelang-operator-dev to inspect this workspace and tell me whether the MCP knowledge base is available."
- "Use tilelang-operator-dev to debug this dtype mismatch. Here is the full error log: ..."
- "I want to target Huawei Ascend 910B. Check whether the local TileLang checkout provides backend evidence before proposing any CANN-specific code."

### Claude Code 应该如何工作

对于代码生成任务，比较合格的回答应当：

- 先展示 retrieval trace，再写代码；
- 说明选中了哪些 TileLang pattern 和 API 记录；
- 给出设备置信度和未解决的硬件问题；
- 只有在 API 符号被确认后才生成代码；
- 给出正确性测试和 benchmark 命令；
- 清楚区分已验证行为和假设。

对于不确定或受限硬件，例如缺少 `tilelang-ascend` 证据的华为昇腾、沐曦、摩尔线程、寒武纪、壁仞、天数智芯或昆仑芯，回答不应臆造厂商 target，而应要求提供后端/编译器证据，或降级为架构无关的设计建议。

## MCP 工具

| 工具 | 用途 |
|------|------|
| `inspect_tilelang_workspace` | 验证算子工作区、TileLang 源码和知识库可用性 |
| `validate_knowledge_base` | 验证交付文件、解析 JSON/JSONL 记录，并在源码可用时审计 evidence 路径 |
| `normalize_device_profile` | 规范化厂商、型号和目标后端 |
| `search_capabilities` | 查找匹配的算子能力类别 |
| `search_patterns` | 检索可复用实现模式；`capability_id` 会通过 `capability_map.related_patterns` 过滤 |
| `search_usage_patterns` | 检索编译、运行、比对和性能测试流程 |
| `lookup_apis` | 确认 TileLang API 签名、模块和可见性 |
| `get_source_chunks` | 从知识库交付内容中获取聚焦的源码回退片段 |
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
| 华为昇腾 | 不从 TileLang 主仓库自动推断目标；只有提供外部 `tilelang-ascend` 仓库或等价后端/编译证据时，才保留用户指定 target | 提供外部后端证据前为受限 |
| 其他加速器厂商：沐曦、摩尔线程、寒武纪、壁仞、天数智芯、昆仑芯 | 不自动推断目标；只有用户提供的 target 且有源码和编译证据时才保留使用 | 受限 |

WGMMA、TCGEN05、TMA、`cp.async`、MFMA、LDS、TMEM、`cluster_dims` 和 `is_cpu=True` 等架构相关特性，必须先通过检索到的知识记录和源码/API 证据确认，再进行推荐。

对于华为昇腾、沐曦、摩尔线程、寒武纪、壁仞、天数智芯、昆仑芯或其他加速器厂商，Skill 可以识别厂商类别，但不能在缺少本地 TileLang backend、compiler、runtime 和示例证据时臆造 CANN、MUSA、MACA、MLU、XPU 或其他厂商 target。TileLang 主仓库 README 提到昇腾支持位于 `tilelang-ascend` 外部仓库；开发昇腾专用算子时，应把该仓库作为源码证据输入。

## 验证

在 `tilelang-operator-dev` 仓库中运行：

```bash
python -m pytest tests/test_mcp_server.py -q
python scripts/tilelang_operator_mcp.py --check
python .claude/skills/run-tilelang-mcp/driver.py --smoke
python scripts/audit_tilelang_knowledge.py --tilelang-source <workspace-root>/tilelang
```

`run-tilelang-mcp` Skill 和 driver 保留用于 MCP 服务开发与 smoke test。它不是默认面向用户的算子开发 Skill。

知识库审计会对照你提供的 TileLang checkout 检查 JSON/JSONL 解析、源码证据路径、行号范围以及官方 `examples/` 目录覆盖情况。

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
