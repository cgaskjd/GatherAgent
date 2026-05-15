# GatherAgent

> **聚六家之长，成一家之言** — The convergence agent born from a deep comparative analysis of 6 leading AI agent projects.

GatherAgent 不是从零开始的又一个 Agent，而是对 DeepSeek-TUI、Claude-Code、Codex、Everything-Claude-Code、Hermes-Agent、OpenClaw 六大项目的深度对比后，取各家之精华、补各家之不足，汇聚而成的统一平台。

---

## 为什么需要 GatherAgent？

| 痛点 | 现有项目的局限 | GatherAgent 的解法 |
|------|---------------|-------------------|
| 模型路由单一 | DeepSeek-TUI 只有 Auto 路由，Hermes 只有 Auxiliary，OpenClaw 只有 Failover | **三层路由合一**：Auto + Auxiliary + Failover 逐层生效 |
| 预算控制粗暴 | Codex 硬上限直接截断，Claude-Code 无 token 预算 | **三级预算**：max_iterations + token_budget + grace_call（宽限调用） |
| 沙箱只覆盖一个层面 | DeepSeek-TUI/Codex 仅 OS 级，Hermes/OpenClaw 仅容器级 | **双层沙箱**：OS 级 + 容器级，按场景自动选择 |
| 无闭环学习 | Claude-Code/Codex 的 Skill 创建后不再演进 | **Curator 生命周期**：创建→使用→改进→归档，永不过时 |
| 会话不可逆 | Claude-Code 一旦改错无法回滚 | **Fork + Snapshot + Restore**：随时分叉、快照、回滚 |
| 协作无结构 | ECC 的 60 个 Agent 无任务板 | **Kanban 看板**：SQLite 状态机 + Dispatcher + Worker |
| 多平台隔离难 | 所有项目共用一套配置 | **Profile 多实例**：`gather -p coder` 完全隔离 |
| 安全策略缺失 | Claude-Code 仅 yes/no 审批 | **DM 配对 + 审批门 + 审计日志** 三层安全 |

---

## 六大项目特性对比

| 特性 | DeepSeek-TUI | Claude-Code | Codex | ECC | Hermes-Agent | OpenClaw | **GatherAgent** |
|------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Auto 模型路由** | ✅ Flash 预路由 | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Auxiliary 任务路由** | ❌ | ❌ | ❌ | ❌ | ✅ 按任务分流 | ❌ | ✅ |
| **Failover 故障切换** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 密钥轮转 | ✅ |
| **三层预算控制** | ❌ 迭代上限 | ❌ 无 | ❌ 硬上限 | ❌ 无 | ✅ grace_call | ❌ 无 | ✅ |
| **OS 级沙箱** | ✅ Seatbelt | ❌ | ✅ Landlock | ❌ | ❌ | ❌ | ✅ |
| **容器沙箱** | ❌ | ❌ | ❌ | ❌ | ✅ Docker/SSH | ✅ Docker/Modal | ✅ |
| **Curator 闭环学习** | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| **会话 Fork** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Side-Git 快照** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Kanban 协作** | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| **FTS5 会话搜索** | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| **Honcho 用户建模** | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| **DM 配对安全** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **审批门** | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Agent-First 委托** | ❌ | ❌ | ❌ | ✅ 60+ Agent | ❌ | ❌ | ✅ |
| **Gateway 网关** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 25+ 渠道 | ✅ |
| **Profile 多实例** | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| **6 主题 TUI** | ✅ | ❌ | ❌ | ❌ | ✅ Skin | ❌ | ✅ |
| **4 语言 i18n** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **跨平台** | ❌ Rust only | ✅ | ❌ Rust only | ✅ | ✅ | ✅ | ✅ |

> GatherAgent 覆盖了所有 6 个项目中 **19 项核心特性**，其中 **9 项是独有创新**（三层路由/三层预算/双层沙箱组合等）。

---

## 架构总览

```
gather/
├── agent/          # 核心循环 + 三层路由 + 三级预算 + 上下文管理
├── tools/          # 自动发现注册 + Toolset 分组 + 条件启用
├── memory/         # 可插拔记忆 + 用户建模 + FTS5 搜索
├── skills/         # Curator 生命周期 + 质量标准 + 市场
├── sandbox/        # OS 级 (Seatbelt/Landlock/Job Objects) + 容器级 (Docker/SSH/Modal)
├── session/        # SQLite+FTS5 + Fork + Side-Git 快照 + Restore
├── gateway/        # 多渠道消息 + 多 Agent 路由 + DM 配对
├── kanban/         # SQLite 看板 + 状态机 + Dispatcher
├── config/         # 多层加载 + Profile 多实例 + schema 校验
├── tui/            # Textual TUI + 6 主题 + 4 语言
├── security/       # 审批门 + DM 配对 + 审计日志
├── providers/      # OpenAI/Anthropic/OpenRouter + Failover + 密钥池
└── cli/            # Click CLI + setup 向导
```

---

## 快速开始

```bash
# 一行安装（Linux/macOS/Windows）
pip install git+https://github.com/CGaskjd/GatherAgent.git

# 或克隆安装
git clone https://github.com/CGaskjd/GatherAgent.git
cd GatherAgent
pip install -e ".[all]"

# 开始使用
gather "explain this function"      # 单次对话
gather --model auto "fix this bug"  # Auto 路由模式
gather -p coder "refactor this"     # Profile 隔离
gather --yolo "deploy it"           # 自动审批模式
gather --tui                        # TUI 界面
gather gateway start                # 启动网关（Telegram/Discord/Slack）
```

Docker 一键运行：

```bash
docker run --rm -it -e OPENAI_API_KEY -v "$PWD:/workspace" cgaskjd/gather-agent
```

---

## 核心创新详解

### 1. 三层模型路由 — 无惧故障、智能降级

```
Layer 0: 显式覆盖（--model gpt-4o --provider anthropic）
    ↓ 无覆盖时
Layer 1: Auxiliary 路由（Hermes-Agent）— 按任务分流
    ↓ 非辅助任务时
Layer 2: Auto 路由（DeepSeek-TUI）— Flash 预路由选模型
    ↓ 默认配置
Layer 3: 默认配置
    ↓ 调用失败时
Failover: 自动切换下一个提供商 + 密钥轮转（OpenClaw）
```

### 2. 三级预算控制 — 不会死循环

```
max_iterations (硬上限) → token_budget (Token 预算) → grace_call (宽限调用)
     90 次                    可选                      预算耗尽后再一次总结
```

### 3. 双层沙箱 — 按需隔离

```
Sandbox mode: auto
├── 本地执行 → OS 级沙箱
│   ├── macOS: Seatbelt (sandbox-exec)
│   ├── Linux: Landlock (kernel 5.13+) / unshare 降级
│   └── Windows: Job Objects (pywin32)
└── 网关/不信任 → 容器沙箱
    ├── Docker (默认)
    ├── SSH 远程
    ├── Modal / Daytona
    └── Singularity (HPC 场景)
```

### 4. 闭环学习循环 — Skill 永不腐烂

```
创建 → 使用 → Curator 检查 → 改进/归档
  ↑                          |
  └──── UserModel 反馈 ──────┘
```

### 5. 会话全生命周期 — 可分叉、可快照、可回滚

```
Fork ─── 分叉到新会话
Snapshot ── Side-Git 每回合自动快照
Restore ── 回滚到任意时间点
Search ─── FTS5 全文搜索历史会话
```

---

## 四种运行模式

| 模式 | 行为 | 来源 |
|------|------|------|
| **Plan** | 只读调查，不执行任何修改操作 | DeepSeek-TUI |
| **Agent** | 交互模式，工具调用需审批门确认 | Claude-Code |
| **YOLO** | 自动审批所有工具，信任工作区使用 | DeepSeek-TUI |
| **Sandbox** | 所有命令在隔离容器中执行 | OpenClaw |

---

## 配置层级

```
~/.gather/config.yaml                    # 全局（最高优先级）
~/.gather/profiles/<name>/config.yaml    # Profile 级（gather -p <name>）
<workspace>/.gather/config.yaml          # 项目级（不能覆盖密钥/提供商）
```

---

## 跨平台支持

| 平台 | Shell | 沙箱 | 安装 |
|------|-------|------|------|
| Linux | bash/sh | Landlock/unshare | `bash scripts/install.sh` |
| macOS | bash/sh | Seatbelt | `bash scripts/install.sh` |
| Windows | PowerShell/cmd | Job Objects | `powershell scripts/install.ps1` |
| Docker | bash | 容器隔离 | `docker run cgaskjd/gather-agent` |

---

## 致谢

GatherAgent 站在巨人的肩膀上，感谢以下项目的启发：

- [DeepSeek-TUI](https://github.com/nicepkg/deepseek-tui) — Auto 路由、前缀缓存、Fork/快照、多主题 TUI
- [Claude-Code](https://github.com/anthropics/claude-code) — 审批门、插件 SDK、IDE 集成
- [Codex](https://github.com/openai/codex) — OS 沙箱、快照测试、构建规范
- [Everything-Claude-Code](https://github.com/anthropics/everything-claude-code) — Agent-First 委托、Hook 引擎、Rule 系统
- [Hermes-Agent](https://github.com/nicepkg/hermes) — Curator 闭环、Honcho 建模、Kanban 协作、Profile 隔离
- [OpenClaw](https://github.com/openclaw/openclaw) — Gateway 网关、DM 配对、Failover 切换、多渠道路由

## License

MIT
