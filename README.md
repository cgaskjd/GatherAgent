# GatherAgent

**The convergence agent** — combining the best innovations from 6 leading AI agent projects into one unified platform.

## Origin: Standing on the Shoulders of Giants

GatherAgent is born from a deep comparative analysis of six AI agent projects:

| Source Project | What We Inherited |
|---|---|
| **DeepSeek-TUI** | Auto model routing, 1M-context prefix cache tracking, RLM low-cost batch analysis, fork+restore sessions, OS-level sandbox, multi-theme TUI, 4-language i18n |
| **Claude-Code** | Plugin SDK architecture, approval gate pattern, IDE integration model |
| **Codex** | Responses API streaming, insta-style snapshot testing, argument comment lint discipline, Bazel-inspired build rigor |
| **Everything-Claude-Code** | Agent-First philosophy, 60-agent delegation pattern, Hook automation engine, Rule system, context budget management |
| **Hermes-Agent** | Closed learning loop (Curator), 8+ memory provider plugins, Honcho user modeling, delegate_task + Kanban collaboration, FTS5 session search, Profile multi-instance, Skin engine, strict Skill quality standards, task-level model routing (auxiliary) |
| **OpenClaw** | 25+ messaging channels, Gateway control plane, Live Canvas + A2UI, voice wake + talk, iOS/Android companion apps, Model failover, DM pairing security, multi-Agent channel routing |

## Architecture

```
gather/
├── agent/          # Core loop + budget + routing + delegation + context
├── tools/          # Auto-discovery registry + toolset grouping + conditional enable
├── memory/         # Pluggable memory providers + user modeling + FTS5 search
├── skills/         # Lifecycle management (Curator) + quality standards + marketplace
├── sandbox/        # OS-level (Seatbelt/Landlock) + Container (Docker/SSH/Modal) + Policy engine
├── session/        # SQLite+FTS5 store + fork + side-git snapshots + restore
├── gateway/        # Multi-channel messaging + multi-Agent routing + DM pairing
├── kanban/         # SQLite-backed collaborative board + dispatcher + worker
├── config/         # Multi-layer loader + Profile multi-instance + schema validation
├── tui/            # Textual TUI + theme engine + i18n (4 languages)
├── security/       # Approval gate + DM pairing + audit trail
├── providers/      # OpenAI-compat + Anthropic + OpenRouter + failover + credential pool
└── cli/            # Click-based CLI + setup wizard
```

## Quick Start

```bash
# Install
pip install -e ".[all]"

# First run — interactive setup
gather setup

# Start chatting
gather

# One-shot
gather "explain this function"

# With model auto-routing
gather --model auto "fix this bug"

# Start gateway (Telegram/Discord/Slack/...)
gather gateway start

# TUI mode
gather --tui
```

## Core Innovations

### 1. Three-Layer Model Router
- **Auto Router** (from DeepSeek-TUI): Flash model pre-routes → selects Pro/Flash + thinking level
- **Auxiliary Router** (from Hermes-Agent): Per-task model assignment (main=GPT-4, curator=Flash, vision=Gemini)
- **Failover Router** (from OpenClaw): Automatic provider switch on failure + credential rotation

### 2. Closed Learning Loop
- **Curator** (from Hermes-Agent): Skills auto-created from experience, improved during use, archived when stale
- **User Modeling** (from Hermes-Agent/Honcho): Dialectic understanding of user preferences across sessions
- **Session Search** (from Hermes-Agent): FTS5 + LLM summarization for cross-session recall

### 3. Dual-Level Sandbox
- **OS-Level** (from DeepSeek-TUI/Codex): Seatbelt (macOS) + Landlock (Linux) + Job Objects (Windows)
- **Container-Level** (from Hermes-Agent/OpenClaw): Docker + SSH + Modal + Daytona backends

### 4. Structured Multi-Agent Collaboration
- **Concurrent Pool** (from DeepSeek-TUI): Non-blocking sub-agents with handle_read result retrieval
- **Kanban Board** (from Hermes-Agent): SQLite-backed task board with state machine + dispatcher
- **Channel Routing** (from OpenClaw): Different channels → different Agent personas

### 5. Full Session Lifecycle
- **Fork** (from DeepSeek-TUI): Branch a session at any turn
- **Side-Git Snapshots** (from DeepSeek-TUI): Auto-snapshot before/after each turn
- **Restore/Undo** (from DeepSeek-TUI + Hermes-Agent): Roll back to any point

### 6. Agent-First Extensibility
- **60+ Agent Delegation** (from ECC): Domain-specialist agents, not just tools
- **Strict Skill Standards** (from Hermes-Agent): ≤60 char description, native tool references only, platform gating
- **Marketplace** (from OpenClaw/DeepSeek-TUI): ClawHub + GitHub install + agentskills.io compatibility

## Modes

| Mode | Behavior |
|---|---|
| **Plan** | Read-only investigation — model explores before making changes |
| **Agent** | Interactive mode — multi-step tool use with approval gates |
| **YOLO** | Auto-approve all tools — for trusted workspaces |
| **Sandbox** | All commands run in isolated container — for untrusted contexts |

## Configuration

Global: `~/.gather/config.yaml`  
Project: `<workspace>/.gather/config.yaml` (cannot override api_key/base_url/provider)  
Profile: `gather -p <name>` → `~/.gather/profiles/<name>/`  

## License

MIT
