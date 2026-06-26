# TileLang Operator Dev

[English](README.md) | **中文**

MCP 驱动的 TileLang 算子开发技能，支持工作区验证、设备感知规划和智能自动检测。

## 特性

- 🔍 **智能自动检测** - 自动查找 TileLang 源码仓库（零配置）
- 🔄 **双工作区模式** - 独立于 TileLang 源码开发算子
- 📚 **内置知识库** - 13 个 MCP 工具，包含预生成的模式、API 和示例
- 🎯 **设备感知规划** - 支持 NVIDIA、AMD、CPU、Apple Silicon 和 WebGPU
- ✅ **验证优先** - 生成代码前强制进行工作区验证
- 🛠️ **开发向导** - 分步引导式算子开发工作流

## 前置条件

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
# 你的项目必须能访问 tilelang/__init__.py（通常通过 pip install）
# 以及至少 src/transform 或 src/op，外加 examples/ 或 testing/ 或 docs/
```

没有有效的 TileLang 工作区，技能会停止并拒绝生成代码。

## 安装

### 快速开始（Claude Code）

```bash
# 1. 克隆技能包
git clone https://github.com/Leafoon/tilelang-operator-dev.git

# 2. 克隆 TileLang（技能验证的工作区）
git clone https://github.com/tile-ai/tilelang.git

# 3. 将技能放入 TileLang 的 .claude/skills/
cp -r tilelang-operator-dev/.claude/skills/run-tilelang-mcp tilelang/.claude/skills/

# 4. 将 MCP 配置复制到 TileLang 工作区
cp tilelang-operator-dev/resources/.mcp.json tilelang/

# 5. 编辑 tilelang/.mcp.json — 设置脚本路径为实际位置

# 6. 在 Claude Code 中打开 tilelang/ 目录，然后说："帮我写一个 H100 的 GEMM 算子"
```

### 独立算子开发（推荐）

使用**双工作区模式**将自定义算子与 TileLang 源码分离：

```bash
# 1. 克隆技能包和 TileLang
git clone https://github.com/Leafoon/tilelang-operator-dev.git
git clone https://github.com/tile-ai/tilelang.git

# 2. 创建算子工作区（复制模板）
cp -r tilelang-operator-dev/resources/operator_template my-operators
cd my-operators

# 3. 在 Claude Code 中打开 — 自动检测会自动找到 TileLang！
claude .
```

**无需配置！** MCP 服务器会自动检测 TileLang 源码，搜索顺序：
1. 兄弟目录 `tilelang/`（最常见）
2. 向上最多 3 级父目录

**目录结构：**
```
my-projects/
├── tilelang/                          # TileLang 源码（不变）
├── tilelang-operator-dev/             # 本技能仓库
└── my-operators/                      # 你的算子！
    ├── .mcp.json                      # MCP 配置
    ├── init_operator.py               # 算子创建工具
    ├── fused_moe/                     # 算子 1
    │   ├── operator.py
    │   ├── test_operator.py
    │   └── benchmark.py
    └── flash_attention_v2/            # 算子 2
        └── ...
```

### 全局安装（任意目录使用）

将技能复制到全局 Claude Code 技能目录：

```bash
git clone https://github.com/Leafoon/tilelang-operator-dev.git
cp -r tilelang-operator-dev/.claude/skills/run-tilelang-mcp ~/.claude/skills/
```

将 MCP 配置复制到你的工作区并设置 `TILELANG_SOURCE_PATH` 环境变量。

> **Windows 用户：** 使用 `.mcp.windows.json` 代替 — 它用 `python` 而非 `python3`：
> ```bash
> cp tilelang-operator-dev/resources/.mcp.windows.json your-workspace/.mcp.json
> ```

> **注意：** 知识库已内置在 MCP 服务器中 — 不需要单独复制 `tilelang_knowledge/`。服务器会自动使用技能包中的 `resources/tilelang_knowledge/` 作为回退。

### 其他 MCP 兼容工具

将 `SKILL.md` 复制到对应技能位置，使用 `resources/.mcp.json` 配置 MCP：

| 工具 | 技能位置 | MCP 配置 |
|------|----------|----------|
| Claude Code | `.claude/skills/` 或 `~/.claude/skills/` | 项目根目录的 `.mcp.json` |
| OpenAI Codex | `.codex-plugin/` | 项目根目录的 `.mcp.json` |
| Cursor | `.cursorrules` 或项目根目录 | 项目根目录的 `.mcp.json` |
| OpenCode | 项目配置 | 项目根目录的 `.mcp.json` |

## 项目结构

```
tilelang-operator-dev/
├── SKILL.md                         # 核心技能指令
├── metadata.json                    # 技能元数据
├── README.md                        # 英文说明
├── README_CN.md                     # 中文说明
├── CHANGELOG.md                     # 版本历史
├── SETUP_GUIDE.md                   # 详细设置指南
├── LICENSE                          # Apache-2.0
├── .gitignore
│
├── .claude/                         # Claude Code 集成
│   └── skills/
│       └── run-tilelang-mcp/        # MCP 服务器驱动技能
│           ├── SKILL.md             # 代理指令
│           └── driver.py            # 冒烟测试 / 工具调用器
│
├── scripts/                         # 可执行脚本
│   └── tilelang_operator_mcp.py     # MCP 服务器（13 个工具）
│
├── resources/                       # 资源文件
│   ├── .mcp.json                    # MCP 配置（Linux/Mac）
│   ├── .mcp.windows.json            # MCP 配置（Windows）
│   ├── tilelang_knowledge/          # 预生成的知识库
│   │   ├── retrieval_plan.md        # 分步检索流程
│   │   ├── capability_map.json      # 能力路由图
│   │   ├── patterns.jsonl           # 可重用的算子模式
│   │   ├── usage_patterns.jsonl     # 调用序列和工作流
│   │   ├── apis.jsonl               # API 签名和可见性
│   │   ├── source_chunks.jsonl      # 源码回退片段
│   │   ├── semantic_graph.json      # 概念/符号/模式关系图
│   │   ├── semantic_graph.mmd       # 人类可读的 Mermaid 图
│   │   ├── manifest.json            # 仓库元数据
│   │   ├── troubleshooting.jsonl    # 常见问题和解决方案
│   │   └── README.md                # 知识库文档
│   ├── operator_template/           # 独立算子开发模板
│   │   ├── .mcp.json                # 预配置的 MCP 配置
│   │   ├── .gitignore               # Git 忽略规则
│   │   ├── README.md                # 模板文档
│   │   ├── init_operator.py         # 工作区初始化脚本
│   │   └── example_operator/        # 示例算子
│   │       ├── operator.py          # 算子实现模板
│   │       ├── test_operator.py     # 测试模板
│   │       ├── benchmark.py         # 基准测试模板
│   │       └── README.md            # 算子文档模板
│   └── assets/
│       └── app-icon.png
│
├── examples/                        # 使用示例
│   ├── basic-gemm.md               # 基本 GEMM 工作流
│   ├── device-adaptation.md        # 设备适配示例
│   └── failure-cases.md            # 错误处理示例
│
└── tests/                           # 测试用例
    ├── test_mcp_server.py           # 自动化 pytest 测试套件（40+ 测试）
    ├── test_cases.md                # 手动测试用例
    └── eval.yaml                    # 评估配置
```

## MCP 工具

MCP 服务器提供 **13 个工具**用于 TileLang 算子开发：

### 核心验证与搜索

| 工具 | 描述 |
|------|------|
| `inspect_tilelang_workspace` | 验证 TileLang 仓库和知识库存在性。支持双工作区模式。 |
| `validate_knowledge_base` | 解析和验证 JSON/JSONL 交付文件。 |
| `normalize_device_profile` | 标准化供应商/型号/目标，不编造未知架构。 |
| `search_capabilities` | 搜索 `capability_map.json` 查找算子能力。 |
| `search_patterns` | 搜索 `patterns.jsonl` 查找算子实现模式。 |
| `search_usage_patterns` | 搜索 `usage_patterns.jsonl` 查找工作流示例。 |
| `lookup_apis` | 搜索 `apis.jsonl` 查找 TileLang API 符号和签名。 |
| `get_source_chunks` | 从 `source_chunks.jsonl` 获取聚焦的回退代码块。 |
| `trace_semantic_graph` | 检查相关的图节点和边。 |
| `build_operator_retrieval_plan` | 构建结构化的算子检索计划。 |

### 质量与指导工具

| 工具 | 描述 |
|------|------|
| `search_troubleshooting` | 搜索故障排除知识库，查找常见问题、错误和解决方案。 |
| `validate_operator_code` | 对 TileLang 算子代码进行静态分析，检查语法、结构和常见问题。 |
| `operator_development_wizard` | 分步引导式 TileLang 算子开发工作流（12 个阶段）。 |

## 标准工作流

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
11. **实现** - 生成代码、解释或验证计划
12. **代码验证** - `validate_operator_code`
13. **故障排除** - `search_troubleshooting`（如果出现错误）

只有第 11 步可以生成最终的算子代码。

## 失败策略

以下情况必须立即停止：

- 当前工作区不是 TileLang 仓库
- `tilelang_knowledge/` 缺失
- 关键交付文件缺失
- JSON/JSONL 解析失败
- 选定的证据路径在当前仓库中不存在

## 设备策略

设备推荐使用交付字段：
- `device_adaptation`
- `device_strategy`
- `device_execution_notes`
- `device_notes`

**对架构特定功能保持保守：**
- WGMMA（仅 NVIDIA，需验证支持）
- TCGEN05（仅 Hopper+）
- TMA（仅 Hopper+）
- `cp.async`（仅 Ampere+）
- MFMA（仅 AMD）
- LDS（AMD 共享内存）
- TMEM（需验证支持）
- `cluster_dims`（仅 Hopper+）
- `is_cpu=True`（仅 CPU 后端）

## 开发

> **注意：** 以下所有命令使用 `python`。部分 Linux 系统可能需要使用 `python3`。

### 运行 MCP 服务器

```bash
python scripts/tilelang_operator_mcp.py --check
```

### 冒烟测试（全部 13 个工具）

```bash
python .claude/skills/run-tilelang-mcp/driver.py --smoke
```

### 列出可用工具

```bash
python .claude/skills/run-tilelang-mcp/driver.py --list
```

### 调用单个工具

```bash
python .claude/skills/run-tilelang-mcp/driver.py --call normalize_device_profile --args '{"vendor":"nvidia","model":"H100","target":"cuda"}'
```

### 原始 JSON-RPC 测试

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python scripts/tilelang_operator_mcp.py
```

### 运行测试

```bash
python -m pytest tests/test_mcp_server.py -v
```

更多手动测试用例见 `tests/test_cases.md`。

## 文档

| 文档 | 描述 |
|------|------|
| [README.md](README.md) | 本文件 - 英文文档 |
| [README_CN.md](README_CN.md) | 中文文档 |
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | 双工作区模式的详细设置指南 |
| [CHANGELOG.md](CHANGELOG.md) | 版本历史和发布说明 |
| [SKILL.md](SKILL.md) | AI 代理的核心技能指令 |
| [examples/](examples/) | 使用示例和工作流 |
| [tests/](tests/) | 测试用例和评估配置 |

## 许可证

Apache-2.0
