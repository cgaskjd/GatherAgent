"""
Three-Layer Model Router

Combines:
- DeepSeek-TUI's Auto mode (Flash router → Pro/Flash + thinking level)
- Hermes-Agent's Auxiliary routing (per-task model assignment)
- OpenClaw's Failover routing (provider failover + credential rotation)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ThinkingLevel(Enum):
    OFF = "off"
    HIGH = "high"
    MAX = "max"


@dataclass
class RouteDecision:
    """The result of model routing — which model, provider, and thinking level to use."""
    model: str
    provider: str
    thinking: str = "off"
    base_url: str | None = None
    api_key: str | None = None
    failover_chain: list[str] = field(default_factory=list)
    cost_estimate: float = 0.0
    is_auto_routed: bool = False


class ModelRouter:
    """
    Three-layer model router that combines the best routing strategies.

    Layer 1 — Auto Router (from DeepSeek-TUI):
        Uses a cheap Flash model to decide which model and thinking level
        to use for the real request. Short tasks stay on Flash, complex
        tasks escalate to Pro.

    Layer 2 — Auxiliary Router (from Hermes-Agent):
        Assigns different models for different tasks (curator, vision,
        embedding, title generation, session search). Each auxiliary task
        can pin its own provider/model/base_url.

    Layer 3 — Failover Router (from OpenClaw):
        When a provider fails, automatically switches to the next in the
        failover chain. Supports credential pool rotation.
    """

    def __init__(self, config: dict, credential_pool: Any = None):
        self._config = config
        self._credential_pool = credential_pool
        self._model_config = config.get("model", {})
        self._failover_config = self._model_config.get("failover", {})
        self._providers: dict[str, Any] = {}  # Lazy-loaded provider instances

    def route(
        self,
        messages: list[dict],
        model_override: str | None = None,
        provider_override: str | None = None,
        mode: str | None = None,
        task: str | None = None,  # auxiliary task name
    ) -> RouteDecision:
        """
        Route to the best model for the current request.

        Priority:
        1. Explicit override (model_override / provider_override)
        2. Auxiliary task routing (if task is specified)
        3. Auto mode routing (if auto_mode is enabled)
        4. Default config routing
        """
        # Layer 0: Explicit override wins
        if model_override and provider_override:
            return RouteDecision(
                model=model_override,
                provider=provider_override,
                thinking=self._model_config.get("thinking", "off"),
            )

        # Layer 1: Auxiliary routing — from Hermes-Agent
        if task and task in self._model_config.get("auxiliary", {}):
            aux = self._model_config["auxiliary"][task]
            return RouteDecision(
                model=aux.get("model", self._model_config.get("default", "gpt-4o")),
                provider=aux.get("provider", self._model_config.get("provider", "openai")),
                thinking=aux.get("thinking", "off"),
            )

        # Layer 2: Auto mode — from DeepSeek-TUI
        if self._model_config.get("auto_mode"):
            return self._auto_route(messages)

        # Layer 3: Default config
        return RouteDecision(
            model=model_override or self._model_config.get("default", "gpt-4o"),
            provider=provider_override or self._model_config.get("provider", "openai"),
            thinking=self._model_config.get("thinking", "off"),
            base_url=self._model_config.get("base_url"),
            failover_chain=self._failover_config.get("chain", []),
        )

    def _auto_route(self, messages: list[dict]) -> RouteDecision:
        """
        Auto mode routing — from DeepSeek-TUI.

        Uses a cheap Flash model to analyze the request and select
        the optimal model + thinking level. Falls back to local heuristic.
        """
        # Heuristic fallback (in production, this would call a Flash router model)
        last_user_msg = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_msg = msg.get("content", "")
                break

        # Simple heuristic: escalate to Pro for complex tasks
        complex_keywords = [
            "debug", "fix", "refactor", "architect", "security",
            "review", "migrate", "design", "implement", "deploy",
        ]
        is_complex = any(kw in last_user_msg.lower() for kw in complex_keywords)

        if is_complex:
            model = self._model_config.get("default", "gpt-4o")
            thinking = "high"
        else:
            model = self._model_config.get("fast_model", "gpt-4o-mini")
            thinking = "off"

        return RouteDecision(
            model=model,
            provider=self._model_config.get("provider", "openai"),
            thinking=thinking,
            is_auto_routed=True,
            failover_chain=self._failover_config.get("chain", []),
        )

    def failover(self, failed_route: RouteDecision, error: Exception) -> RouteDecision | None:
        """
        Failover routing — from OpenClaw.

        When a provider fails, try the next provider in the failover chain.
        Returns None if all providers have been exhausted.
        """
        chain = failed_route.failover_chain
        current_provider = failed_route.provider

        if current_provider in chain:
            idx = chain.index(current_provider)
            remaining = chain[idx + 1:]
        else:
            remaining = chain

        if not remaining:
            logger.error(f"All failover providers exhausted. Last error: {error}")
            return None

        next_provider = remaining[0]
        logger.warning(
            f"Failing over from {current_provider} to {next_provider} "
            f"due to: {error}"
        )

        # Map provider to default model
        provider_models = {
            "openai": "gpt-4o",
            "anthropic": "claude-sonnet-4-20250514",
            "openrouter": "openai/gpt-4o",
        }

        return RouteDecision(
            model=provider_models.get(next_provider, "gpt-4o"),
            provider=next_provider,
            thinking=failed_route.thinking,
            failover_chain=remaining,
        )

    def get_provider(self, provider_name: str):
        """Get or create a provider instance."""
        if provider_name not in self._providers:
            # Lazy load provider — in production this would import dynamically
            logger.info(f"Loading provider: {provider_name}")
            self._providers[provider_name] = None  # Placeholder
        return self._providers[provider_name]
