# GatherAgent — Development Guide

Instructions for AI coding assistants and developers working on the GatherAgent codebase.

## Project Type: Python 3.11+

### Commands
- Install: `pip install -e ".[dev]"`
- Run: `gather` (entry point from pyproject.toml)
- Test: `scripts/run_tests.sh` (enforces hermetic CI parity)
- Lint: `ruff check gather/`
- Format: `ruff format gather/`
- Type check: `mypy gather/`

### Architecture Principles

1. **Agent-First** (from ECC): Delegate to specialist agents for domain tasks; tools are the fallback, not the default
2. **Cost-Aware** (from DeepSeek-TUI): Every LLM call is tracked; use cheap models for routing/summarization, expensive models for deep reasoning
3. **Convention Over Configuration** (from Hermes-Agent): Auto-discovery for tools/skills/plugins; no manual registries
4. **Sandbox by Default** (from Codex/OpenClaw): Untrusted contexts auto-sandbox; trust is opt-in
5. **Closed Learning Loop** (from Hermes-Agent): Skills are created, used, improved, and eventually archived — never static
6. **Failover Resilient** (from OpenClaw): Model providers fail over automatically; credential pools rotate

### File Dependency Chain

```
gather/config/loader.py          # No deps — imported by everything
       ↑
gather/tools/registry.py         # No deps — auto-discovery at import time
       ↑
gather/providers/*.py            # Provider adapters, registered at import
       ↑
gather/agent/router.py           # Model routing logic
       ↑
gather/agent/core.py             # Agent loop (depends on router, tools, budget)
       ↑
gather/agent/delegation.py       # Sub-agent management
       ↑
gather/cli/main.py               # CLI entry point
```

### Key Design Patterns

#### Tool Registration (from Hermes-Agent)
Any `gather/tools/*.py` file with a top-level `registry.register()` call is auto-discovered.
Tools are only exposed to the model if: (1) they appear in a toolset, and (2) their `check_fn` passes.

#### Three-Layer Model Router
1. **Auto Router**: Flash model decides Pro/Flash + thinking level per turn
2. **Auxiliary Router**: Per-task model assignment (curator/vision/embedding/search)
3. **Failover Router**: Provider failover chain + credential rotation

#### Budget Control (from Hermes-Agent)
Three-level iteration control:
- `max_iterations`: Hard cap on API calls (default: 90)
- `iteration_budget`: Token budget for the session
- `grace_call`: One final call after budget exhaustion for summarization

#### Skill Quality Standards (from Hermes-Agent)
- `description` ≤ 60 characters, one sentence, no marketing words
- Tool references must use native tool names, not shell pipelines
- `platforms` field must be audited against actual script imports
- Tests in `tests/skills/test_<name>_skill.py`

#### Session Lifecycle (from DeepSeek-TUI)
- `fork <session_id>`: Branch a session at any turn
- Side-git snapshots before/after every turn (stored in `.gather/snapshots/`)
- `/restore` and `/undo` to roll back

#### Profile Multi-Instance (from Hermes-Agent)
- `gather -p <name>` sets GATHER_HOME to `~/.gather/profiles/<name>/`
- All `get_gather_home()` references auto-scope to the active profile
- NEVER hardcode `~/.gather` — always use `get_gather_home()`

### Important Rules

- **NEVER** modify core files (`agent/core.py`, `cli/main.py`, `gateway/core.py`) from plugins
- **NEVER** hardcode `~/.gather` paths — use `get_gather_home()` from `gather.config`
- **NEVER** write change-detector tests — test behavior, not snapshots of data
- **ALWAYS** use `scripts/run_tests.sh` — not `pytest` directly
- **ALWAYS** run `ruff format` after code changes
- **ALWAYS** add `/*param_name*/` comments before opaque literal arguments

### Modes
- **Plan**: Read-only investigation, no tool execution beyond read/search
- **Agent**: Interactive with approval gates (default)
- **YOLO**: Auto-approve all tools
- **Sandbox**: All commands in container isolation
