# GatherAgent

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE) [![GitHub](https://img.shields.io/badge/GitHub-CGaskjd%2FGatherAgent-black.svg)](https://github.com/CGaskjd/GatherAgent)

> **Converging the best of six into one** — The AI agent born from a deep comparative analysis of 6 leading AI agent projects.

---

## Quick Install

```bash
pip install git+https://github.com/CGaskjd/GatherAgent.git
```

Start using immediately:

```bash
gather "explain this function"       # One-shot query
gather                               # Launch interactive TUI
```

<details>
<summary><b>Other Install Methods</b></summary>

```bash
# Clone & editable install (recommended for developers)
git clone https://github.com/CGaskjd/GatherAgent.git
cd GatherAgent
pip install -e ".[all]"

# Linux/macOS one-line script
bash scripts/install.sh

# Windows one-line script
powershell -ExecutionPolicy Bypass -File scripts/install.ps1

# Docker
docker run --rm -it -e OPENAI_API_KEY -v "$PWD:/workspace" cgaskjd/gather-agent
```

</details>

<details>
<summary><b>Quick Configuration</b></summary>

```bash
# Set API key (first-time setup)
export OPENAI_API_KEY=sk-xxx         # Linux/macOS
set OPENAI_API_KEY=sk-xxx            # Windows CMD
$env:OPENAI_API_KEY="sk-xxx"         # Windows PowerShell

# Or use the interactive wizard
gather setup

# Check environment
gather doctor
```

</details>

---

## Usage Examples

```bash
# Basic usage
gather "explain this function"           # One-shot query

# Model selection
gather -m gpt-4o "fix this bug"          # Specify OpenAI GPT-4o
gather --provider anthropic "review"     # Use Claude Sonnet 4
gather --provider openrouter -m google/gemini-2.0-flash "hi"  # Any model via OpenRouter

# Auto routing (Flash pre-router -> smart model + thinking level)
gather --model auto "refactor this module"

# Run modes
gather --yolo "deploy it"                # YOLO mode (auto-approve all tools)
gather -p coder "implement API"          # Profile isolation (independent config/memory/skills)

# Interactive TUI (default when no arguments)
gather                                   # Launch TUI with 6 themes + 4 languages

# Gateway mode (Telegram/Discord/Slack)
gather gateway start

# Built-in commands
gather setup                             # Interactive setup wizard
gather doctor                            # Check environment and dependencies
gather models                            # List available model providers
```

---

## Why GatherAgent?

| Pain Point | Existing Limitation | GatherAgent Solution |
|------|---------------|-------------------|
| Single model routing | DeepSeek-TUI only has Auto, Hermes only Auxiliary, OpenClaw only Failover | **3-Layer Routing**: Auto + Auxiliary + Failover cascading |
| Crude budget control | Codex hard-cuts at limit, Claude-Code has no token budget | **3-Level Budget**: max_iterations + token_budget + grace_call |
| Single-layer sandbox | DeepSeek-TUI/Codex OS-level only, Hermes/OpenClaw container only | **Dual-Layer Sandbox**: OS-level + Container-level, auto-selected |
| No closed-loop learning | Claude-Code/Codex skills never evolve after creation | **Curator Lifecycle**: Create > Use > Improve > Archive |
| Irreversible sessions | Claude-Code can't rollback once a mistake is made | **Fork + Snapshot + Restore**: Branch, snapshot, rollback anytime |
| Unstructured collaboration | ECC's 60 agents have no task board | **Kanban Board**: SQLite state machine + Dispatcher + Worker |
| Hard multi-instance isolation | All projects share one config | **Profile Multi-Instance**: `gather -p coder` fully isolated |
| Missing security policy | Claude-Code only yes/no approval | **DM Pairing + Approval Gate + Audit Log** triple security |

---

## Feature Comparison Across 6 Projects

| Feature | DeepSeek-TUI | Claude-Code | Codex | ECC | Hermes-Agent | OpenClaw | **GatherAgent** |
|------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Auto Model Routing** | Yes (Flash pre-route) | - | - | - | - | - | Yes |
| **Auxiliary Task Routing** | - | - | - | - | Yes (task split) | - | Yes |
| **Failover Switch** | - | - | - | - | - | Yes (key rotation) | Yes |
| **3-Level Budget Control** | - (iter cap) | - (none) | - (hard cap) | - (none) | Yes (grace_call) | - (none) | Yes |
| **OS-Level Sandbox** | Yes (Seatbelt) | - | Yes (Landlock) | - | - | - | Yes |
| **Container Sandbox** | - | - | - | - | Yes (Docker/SSH) | Yes (Docker/Modal) | Yes |
| **Curator Closed-Loop Learning** | - | - | - | - | Yes | - | Yes |
| **Session Fork** | Yes | - | - | - | - | - | Yes |
| **Side-Git Snapshot** | Yes | - | - | - | - | - | Yes |
| **Kanban Collaboration** | - | - | - | - | Yes | - | Yes |
| **FTS5 Session Search** | - | - | - | - | Yes | - | Yes |
| **Honcho User Modeling** | - | - | - | - | Yes | - | Yes |
| **DM Pairing Security** | - | - | - | - | - | Yes | Yes |
| **Approval Gate** | - | Yes | - | - | - | - | Yes |
| **Agent-First Delegation** | - | - | - | Yes (60+ agents) | - | - | Yes |
| **Gateway** | - | - | - | - | - | Yes (25+ channels) | Yes |
| **Profile Multi-Instance** | - | - | - | - | Yes | - | Yes |
| **6-Theme TUI** | Yes | - | - | - | Yes (Skin) | - | Yes |
| **4-Language i18n** | Yes | - | - | - | - | - | Yes |
| **Cross-Platform** | - (Rust only) | Yes | - (Rust only) | Yes | Yes | Yes | Yes |

> GatherAgent covers all **19 core features** across 6 projects, with **9 unique innovations** (3-layer routing / 3-level budget / dual-sandbox combo, etc.).

---

## Architecture Overview

```
gather/
├── agent/          # Core loop + 3-layer routing + 3-level budget + context management
├── tools/          # Auto-discovery registry + Toolset grouping + conditional enablement
├── memory/         # Pluggable memory + user modeling + FTS5 search
├── skills/         # Curator lifecycle + quality standards + marketplace
├── sandbox/        # OS-level (Seatbelt/Landlock/Job Objects) + Container-level (Docker/SSH/Modal)
├── session/        # SQLite+FTS5 + Fork + Side-Git snapshot + Restore
├── gateway/        # Multi-channel messaging + multi-agent routing + DM pairing
├── kanban/         # SQLite board + state machine + Dispatcher
├── config/         # Multi-layer loading + Profile multi-instance + schema validation
├── tui/            # Textual TUI + 6 themes + 4 languages
├── security/       # Approval gate + DM pairing + audit log
├── providers/      # OpenAI/Anthropic/OpenRouter + Failover + key pool
└── cli/            # Click CLI + setup wizard
```

---

## Core Innovations

### 1. 3-Layer Model Routing — Fault-Tolerant, Smart Degradation

```
Layer 0: Explicit override (--model gpt-4o --provider anthropic)
    ↓ no override
Layer 1: Auxiliary routing (from Hermes-Agent) — per-task dispatch
    ↓ non-auxiliary task
Layer 2: Auto routing (from DeepSeek-TUI) — Flash pre-router picks model
    ↓ default config
Layer 3: Default configuration
    ↓ on call failure
Failover: Auto-switch to next provider + key rotation (from OpenClaw)
```

### 2. 3-Level Budget Control — No Infinite Loops

```
max_iterations (hard cap) → token_budget (Token budget) → grace_call (grace call)
     90 turns                    optional                    one final summary after budget exhausted
```

### 3. Dual-Layer Sandbox — Isolation On Demand

```
Sandbox mode: auto
├── Local execution → OS-level sandbox
│   ├── macOS: Seatbelt (sandbox-exec)
│   ├── Linux: Landlock (kernel 5.13+) / unshare fallback
│   └── Windows: Job Objects (pywin32)
└── Gateway / untrusted → Container sandbox
    ├── Docker (default)
    ├── SSH remote
    ├── Modal / Daytona
    └── Singularity (HPC scenarios)
```

### 4. Closed-Loop Learning — Skills That Never Rot

```
Create → Use → Curator check → Improve / Archive
  ↑                                |
  └──── UserModel feedback ───────┘
```

### 5. Full Session Lifecycle — Fork, Snapshot, Rollback

```
Fork    ─── Branch to a new session
Snapshot ── Side-Git auto-snapshot per turn
Restore  ── Rollback to any point in time
Search   ─── FTS5 full-text search across session history
```

---

## Four Run Modes

| Mode | Behavior | Origin |
|------|----------|--------|
| **Plan** | Read-only investigation, no modifications allowed | DeepSeek-TUI |
| **Agent** | Interactive mode, tool calls require approval gate | Claude-Code |
| **YOLO** | Auto-approve all tools, for trusted workspaces | DeepSeek-TUI |
| **Sandbox** | All commands executed in isolated containers | OpenClaw |

---

## Configuration Hierarchy

```
~/.gather/config.yaml                    # Global (highest priority)
~/.gather/profiles/<name>/config.yaml    # Profile level (gather -p <name>)
<workspace>/.gather/config.yaml          # Project level (cannot override keys/providers)
```

---

## Cross-Platform Support

| Platform | Shell | Sandbox | Install |
|----------|-------|---------|--------|
| Linux | bash/sh | Landlock/unshare | `bash scripts/install.sh` |
| macOS | bash/sh | Seatbelt | `bash scripts/install.sh` |
| Windows | PowerShell/cmd | Job Objects | `powershell scripts/install.ps1` |
| Docker | bash | Container isolation | `docker run cgaskjd/gather-agent` |

---

## Acknowledgments

GatherAgent stands on the shoulders of giants. Credit to the following projects for inspiration:

- [DeepSeek-TUI](https://github.com/nicepkg/deepseek-tui) — Auto routing, prefix cache, Fork/snapshot, multi-theme TUI
- [Claude-Code](https://github.com/anthropics/claude-code) — Approval gate, plugin SDK, IDE integration
- [Codex](https://github.com/openai/codex) — OS sandbox, snapshot testing, build specs
- [Everything-Claude-Code](https://github.com/anthropics/everything-claude-code) — Agent-First delegation, Hook engine, Rule system
- [Hermes-Agent](https://github.com/nicepkg/hermes) — Curator closed-loop, Honcho modeling, Kanban collaboration, Profile isolation
- [OpenClaw](https://github.com/openclaw/openclaw) — Gateway, DM pairing, Failover switching, multi-channel routing

## License

MIT
