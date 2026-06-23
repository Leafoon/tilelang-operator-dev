# TileLang Operator Dev

[English](README.md) | **中文**

MCP 驱动的 TileLang 算子开发技能，支持工作区验证和设备感知规划。

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

### 全局安装（任意目录使用）

将技能复制到全局 Claude Code 技能目录：

```bash
git clone https://github.com/Leafoon/tilelang-operator-dev.git
cp -r tilelang-operator-dev/.claude/skills/run-tilelang-mcp ~/.claude/skills/
```

将 MCP 配置复制到你的 TileLang 工作区：

```bash
cp tilelang-operator-dev/resources/.mcp.json your-workspace/
```

编辑 `.mcp.json`，将路径改为 `scripts/tilelang_operator_mcp.py` 的实际位置。

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
│   └── tilelang_operator_mcp.py     # MCP 服务器
│
├── resources/                       # 资源文件
│   ├── .mcp.json                    # MCP 配置（Linux/Mac）
│   ├── .mcp.windows.json            # MCP 配置（Windows）
│   ├── tilelang_knowledge/          # 预生成的知识库
│   │   ├── retrieval_plan.md
│   │   ├── capability_map.json
│   │   ├── patterns.jsonl
│   │   ├── usage_patterns.jsonl
│   │   ├── apis.jsonl
│   │   ├── source_chunks.jsonl
│   │   ├── semantic_graph.json
│   │   ├── semantic_graph.mmd
│   │   ├── manifest.json
│   │   └── README.md
│   └── assets/
│       └── app-icon.png
│
├── examples/                        # 使用示例
│   ├── basic-gemm.md
│   ├── device-adaptation.md
│   └── failure-cases.md
│
└── tests/                           # 测试用例
    ├── test_mcp_server.py           # 自动化 pytest 测试套件
    ├── test_cases.md
    └── eval.yaml
```

## 文件说明

| 文件 | 用途 | 谁读它 |
|------|------|--------|
| `SKILL.md` | AI 代理指令（何时/如何使用工具） | AI 代理（Claude、GPT 等） |
| `metadata.json` | 技能元数据（版本、作者等） | AI 工具、包管理器 |
| `.claude/skills/run-tilelang-mcp/SKILL.md` | MCP 驱动技能指令 | Claude Code（自动加载） |
| `.claude/skills/run-tilelang-mcp/driver.py` | MCP 服务器冒烟测试和工具调用器 | 开发者、CI/CD |
| `scripts/tilelang_operator_mcp.py` | MCP 服务器实现 | AI 工具运行时 |
| `resources/.mcp.json` | MCP 服务器连接配置 | AI 工具（Claude Code、Codex 等） |
| `resources/tilelang_knowledge/` | 预生成的知识库 | MCP 服务器 |
| `examples/` | 使用示例 | 开发者 |
| `tests/` | 测试用例和评估配置 | CI/CD、开发者 |

## MCP 工具

MCP 服务器提供以下工具：

- `inspect_tilelang_workspace`：验证 TileLang 仓库和交付目录
- `validate_knowledge_base`：解析并统计 JSON/JSONL 交付文件
- `normalize_device_profile`：规范化 vendor/model/target，不编造未知架构
- `search_capabilities`：搜索 `capability_map.json`
- `search_patterns`：搜索 `patterns.jsonl`
- `search_usage_patterns`：搜索 `usage_patterns.jsonl`
- `lookup_apis`：搜索 `apis.jsonl`
- `get_source_chunks`：检索 `source_chunks.jsonl` 中的回退代码块
- `trace_semantic_graph`：检查相关图节点和边
- `build_operator_retrieval_plan`：构建结构化算子检索计划

## 标准工作流

1. 使用 `inspect_tilelang_workspace` 验证工作区
2. 使用 `validate_knowledge_base` 验证交付文件
3. 使用 `normalize_device_profile` 规范目标设备
4. 搜索能力、模式、用法、API 和源代码块层
5. 仅在需要依赖或关系时追踪语义图
6. 使用检索到的证据生成算子计划、代码、解释和验证计划
7. 当证据缺失或不一致时停止，而不是猜测

## 失败策略

以下情况必须停止：

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

对 WGMMA、TCGEN05、TMA、`cp.async`、MFMA、LDS、TMEM、`cluster_dims` 和 `is_cpu=True` 保持保守。

## 开发

> **注意：** 以下所有命令使用 `python`。部分 Linux 系统可能需要使用 `python3`。

### 运行 MCP 服务器

```bash
python scripts/tilelang_operator_mcp.py --check
```

### 冒烟测试（全部 10 个工具）

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

## 许可证

Apache-2.0
