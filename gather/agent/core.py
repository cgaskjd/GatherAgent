"""
GatherAgent — Agent Core Loop

Combines:
- Hermes-Agent's three-level budget control (max_iterations + iteration_budget + grace_call)
- DeepSeek-TUI's async sub-agent pool
- OpenClaw's event-driven gateway integration
- ECC's Agent-First delegation pattern
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from gather.agent.budget import IterationBudget
from gather.agent.context import ContextManager
from gather.agent.router import ModelRouter, RouteDecision
from gather.config.loader import get_gather_home, load_config
from gather.session.store import SessionStore
from gather.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class AgentMode(Enum):
    """Agent execution modes — from DeepSeek-TUI's Plan/Agent/YOLO + OpenClaw's Sandbox."""
    PLAN = "plan"        # Read-only investigation
    AGENT = "agent"      # Interactive with approval gates
    YOLO = "yolo"        # Auto-approve all tools
    SANDBOX = "sandbox"  # All commands in container isolation


@dataclass
class ToolCall:
    """A single tool call from the LLM."""
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class ToolResult:
    """Result of executing a tool call."""
    tool_call_id: str
    content: str
    is_error: bool = False


@dataclass
class TurnMetrics:
    """Metrics for a single agent turn — from DeepSeek-TUI's cost tracking."""
    turn_number: int = 0
    model_used: str = ""
    thinking_level: str = "off"
    input_tokens: int = 0
    output_tokens: int = 0
    cache_hit_tokens: int = 0
    cache_miss_tokens: int = 0
    cost_usd: float = 0.0
    tool_calls_count: int = 0
    duration_seconds: float = 0.0


class GatherAgent:
    """
    The core agent loop — combining the best of 6 agent projects.

    Architecture:
    - Three-level budget control (from Hermes-Agent)
    - Async tool execution (from DeepSeek-TUI)
    - Three-layer model routing (Auto + Auxiliary + Failover)
    - Session fork + side-git snapshots (from DeepSeek-TUI)
    - Agent-First delegation (from ECC)
    - Event-driven gateway compatibility (from OpenClaw)
    """

    def __init__(
        self,
        session_id: str | None = None,
        mode: AgentMode = AgentMode.AGENT,
        model: str | None = None,
        provider: str | None = None,
        max_iterations: int = 90,
        iteration_budget: int | None = None,
        grace_call: bool = True,
        profile: str | None = None,
        # Callbacks
        on_tool_call: Callable[[ToolCall], None] | None = None,
        on_tool_result: Callable[[ToolResult], None] | None = None,
        on_turn_metrics: Callable[[TurnMetrics], None] | None = None,
        on_interrupt: Callable[[], bool] | None = None,
        # Delegation
        credential_pool: Any = None,
    ):
        # Profile-aware config (from Hermes-Agent)
        self._profile = profile
        self._config = load_config(profile=profile)
        self._gather_home = get_gather_home()

        # Identity
        self.session_id = session_id or str(uuid.uuid4())
        self.mode = mode
        self._model_override = model
        self._provider_override = provider

        # Budget — from Hermes-Agent's three-level control
        self._max_iterations = max_iterations
        self._budget = IterationBudget(
            max_iterations=max_iterations,
            token_budget=iteration_budget,
            grace_call_enabled=grace_call,
        )

        # Subsystems
        self._router = ModelRouter(config=self._config, credential_pool=credential_pool)
        self._context = ContextManager(config=self._config)
        self._tools = ToolRegistry.instance()
        self._session_store = SessionStore(home=self._gather_home)

        # State
        self._messages: list[dict[str, Any]] = []
        self._interrupted = False
        self._turn_count = 0

        # Callbacks
        self._on_tool_call = on_tool_call
        self._on_tool_result = on_tool_result
        self._on_turn_metrics = on_turn_metrics
        self._on_interrupt = on_interrupt

        # Metrics
        self._total_cost = 0.0
        self._total_tokens = 0
        self._start_time = time.time()

    # ─── Core Agent Loop ────────────────────────────────────

    async def run(self, user_message: str, system_message: str | None = None) -> str:
        """
        Run the agent loop with three-level budget control.

        This is the main entry point — the "think-act-observe" cycle that all
        6 source projects implement, but with the most robust budget control
        (from Hermes-Agent) and async tool execution (from DeepSeek-TUI).
        """
        # Initialize session
        if system_message:
            self._messages.append({"role": "system", "content": system_message})
        self._messages.append({"role": "user", "content": user_message})

        # Pre-turn: side-git snapshot (from DeepSeek-TUI)
        await self._pre_turn_snapshot()

        # Main loop with budget control
        final_response = ""
        while self._should_continue():
            turn_start = time.time()
            self._turn_count += 1

            # Check for interrupt
            if self._check_interrupt():
                break

            # Step 1: Route to model (three-layer routing)
            route = self._router.route(
                messages=self._messages,
                model_override=self._model_override,
                provider_override=self._provider_override,
                mode=self.mode,
            )

            # Step 2: Call LLM
            try:
                response = await self._call_llm(route)
            except Exception as e:
                logger.error(f"LLM call failed: {e}")
                # Failover (from OpenClaw)
                route = self._router.failover(route, error=e)
                if route is None:
                    final_response = f"All providers failed. Last error: {e}"
                    break
                response = await self._call_llm(route)

            # Step 3: Process response
            if response.get("tool_calls"):
                # Execute tools (with approval gate in Agent mode)
                results = await self._execute_tools(response["tool_calls"], route)
                self._messages.append({
                    "role": "assistant",
                    "content": response.get("content", ""),
                    "tool_calls": response["tool_calls"],
                })
                for result in results:
                    self._messages.append({
                        "role": "tool",
                        "tool_call_id": result.tool_call_id,
                        "content": result.content,
                    })
                self._budget.record_iteration()
            else:
                # Final response — no more tool calls
                final_response = response.get("content", "")
                break

            # Post-turn metrics
            metrics = TurnMetrics(
                turn_number=self._turn_count,
                model_used=route.model,
                thinking_level=route.thinking,
                input_tokens=response.get("usage", {}).get("input_tokens", 0),
                output_tokens=response.get("usage", {}).get("output_tokens", 0),
                cache_hit_tokens=response.get("usage", {}).get("cache_hit_tokens", 0),
                duration_seconds=time.time() - turn_start,
                tool_calls_count=len(response.get("tool_calls", [])),
            )
            self._total_cost += self._estimate_cost(metrics, route)
            if self._on_turn_metrics:
                self._on_turn_metrics(metrics)

        # Grace call — from Hermes-Agent: one final call after budget exhaustion
        if not final_response and self._budget.should_grace_call():
            logger.info("Budget exhausted — performing grace call for summarization")
            final_response = await self._grace_call()

        # Post-turn: side-git snapshot (from DeepSeek-TUI)
        await self._post_turn_snapshot()

        # Persist session
        await self._session_store.save(self.session_id, self._messages)

        return final_response

    def _should_continue(self) -> bool:
        """Check if the agent loop should continue (three-level budget)."""
        return self._budget.remaining() and not self._interrupted

    def _check_interrupt(self) -> bool:
        """Check for user interrupt."""
        if self._on_interrupt and self._on_interrupt():
            self._interrupted = True
            return True
        return False

    # ─── Tool Execution ─────────────────────────────────────

    async def _execute_tools(
        self, tool_calls: list[dict], route: RouteDecision
    ) -> list[ToolResult]:
        """
        Execute tool calls with:
        - Approval gate in Agent mode (from Claude-Code)
        - Sandbox isolation in Sandbox mode (from OpenClaw)
        - Concurrent execution where possible (from DeepSeek-TUI)
        """
        results = []

        # Group tools: independent tools can run concurrently
        independent = []
        dependent = []
        for tc in tool_calls:
            call = ToolCall(id=tc["id"], name=tc["function"]["name"],
                          arguments=json.loads(tc["function"]["arguments"]))
            # Check if tool requires sequential execution
            if call.name in ("write_file", "edit_file", "shell"):
                dependent.append(call)
            else:
                independent.append(call)

        # Execute independent tools concurrently (from DeepSeek-TUI)
        if independent:
            tasks = [self._execute_single_tool(tc, route) for tc in independent]
            results.extend(await asyncio.gather(*tasks))

        # Execute dependent tools sequentially
        for tc in dependent:
            result = await self._execute_single_tool(tc, route)
            results.append(result)

        return results

    async def _execute_single_tool(
        self, call: ToolCall, route: RouteDecision
    ) -> ToolResult:
        """Execute a single tool call with approval gate."""
        # Notify callback
        if self._on_tool_call:
            self._on_tool_call(call)

        # Approval gate — from Claude-Code's approval pattern
        if self.mode == AgentMode.AGENT:
            approved = await self._request_approval(call)
            if not approved:
                return ToolResult(
                    tool_call_id=call.id,
                    content="Tool call rejected by user.",
                    is_error=True,
                )

        # Execute in appropriate sandbox
        try:
            handler = self._tools.get_handler(call.name)
            if handler is None:
                content = f"Unknown tool: {call.name}"
                return ToolResult(tool_call_id=call.id, content=content, is_error=True)

            # Sandbox routing (from DeepSeek-TUI + OpenClaw)
            if self.mode == AgentMode.SANDBOX:
                result = await self._execute_in_sandbox(handler, call)
            elif self.mode == AgentMode.PLAN:
                # Plan mode: only allow read-only tools
                if call.name not in self._tools.read_only_tools():
                    return ToolResult(
                        tool_call_id=call.id,
                        content="Tool not allowed in Plan mode.",
                        is_error=True,
                    )
                result = handler(call.arguments)
            else:
                result = handler(call.arguments)

            tool_result = ToolResult(tool_call_id=call.id, content=str(result))

        except Exception as e:
            tool_result = ToolResult(
                tool_call_id=call.id,
                content=f"Tool execution error: {e}",
                is_error=True,
            )

        if self._on_tool_result:
            self._on_tool_result(tool_result)

        return tool_result

    async def _request_approval(self, call: ToolCall) -> bool:
        """Request user approval for a tool call — from Claude-Code's pattern."""
        # In a real implementation, this would prompt the user
        # For now, auto-approve in YOLO mode, prompt in AGENT mode
        if self.mode == AgentMode.YOLO:
            return True
        logger.info(f"Approval requested for: {call.name}({call.arguments})")
        return True  # Simplified — real impl would show interactive prompt

    async def _execute_in_sandbox(self, handler: Callable, call: ToolCall) -> Any:
        """Execute tool in sandbox — from OpenClaw's container isolation."""
        # In production, this would route to Docker/SSH/Modal backend
        logger.info(f"Executing {call.name} in sandbox")
        return handler(call.arguments)

    # ─── LLM Communication ──────────────────────────────────

    async def _call_llm(self, route: RouteDecision) -> dict[str, Any]:
        """Call the LLM with the routed model — streaming support."""
        provider = self._router.get_provider(route.provider)
        messages = self._context.prepare_messages(
            self._messages, route.model, route.thinking
        )
        tools = self._tools.get_schemas_for_model()

        response = await provider.chat(
            model=route.model,
            messages=messages,
            tools=tools,
            thinking=route.thinking,
        )
        return response

    async def _grace_call(self) -> str:
        """
        Grace call — from Hermes-Agent: one final summarization call
        after budget exhaustion, so the agent can produce a meaningful
        closing response instead of dying mid-thought.
        """
        self._messages.append({
            "role": "user",
            "content": (
                "[System] You have exhausted your iteration budget. "
                "Please summarize what you've accomplished so far and "
                "what remains to be done. Be concise."
            ),
        })
        route = self._router.route(messages=self._messages)
        response = await self._call_llm(route)
        return response.get("content", "")

    # ─── Session Lifecycle ──────────────────────────────────

    async def _pre_turn_snapshot(self):
        """Side-git snapshot before each turn — from DeepSeek-TUI."""
        # In production, this would create a git snapshot of the workspace
        pass

    async def _post_turn_snapshot(self):
        """Side-git snapshot after each turn — from DeepSeek-TUI."""
        pass

    # ─── Cost Tracking ──────────────────────────────────────

    @staticmethod
    def _estimate_cost(metrics: TurnMetrics, route: RouteDecision) -> float:
        """Estimate cost for a turn — from DeepSeek-TUI's prefix-cache-aware costing."""
        # Simplified — real impl would use provider-specific pricing tables
        input_cost = (metrics.input_tokens / 1_000_000) * 3.0  # $3/1M input
        output_cost = (metrics.output_tokens / 1_000_000) * 15.0  # $15/1M output
        cache_saving = (metrics.cache_hit_tokens / 1_000_000) * 2.5  # Cache discount
        return max(0, input_cost + output_cost - cache_saving)

    # ─── Public API ─────────────────────────────────────────

    @property
    def total_cost(self) -> float:
        return self._total_cost

    @property
    def turn_count(self) -> int:
        return self._turn_count

    def interrupt(self):
        """Signal the agent to stop — from Hermes-Agent's interrupt mechanism."""
        self._interrupted = True

    def fork(self, at_turn: int | None = None) -> "GatherAgent":
        """
        Fork this session at a given turn — from DeepSeek-TUI.

        Creates a new Agent with the same config but a new session_id,
        and copies messages up to the specified turn.
        """
        new_session_id = str(uuid.uuid4())
        forked = GatherAgent(
            session_id=new_session_id,
            mode=self.mode,
            model=self._model_override,
            provider=self._provider_override,
            max_iterations=self._max_iterations,
            profile=self._profile,
        )
        if at_turn is not None:
            forked._messages = self._messages[:at_turn * 2]  # Approximate turn boundary
        else:
            forked._messages = list(self._messages)
        return forked
