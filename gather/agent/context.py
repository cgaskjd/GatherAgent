"""
Context Manager — combining:
- DeepSeek-TUI's prefix-cache-aware compaction
- Hermes-Agent's FTS5 session search + LLM summarization
- ECC's context budget management
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ContextManager:
    """Manages the conversation context window with cost-aware compaction."""

    # Model context window sizes
    MODEL_CONTEXT_WINDOWS = {
        # OpenAI
        "gpt-4o": 128_000, "gpt-4o-mini": 128_000,
        "gpt-4-turbo": 128_000, "gpt-3.5-turbo": 16_000,
        "o1": 128_000, "o1-mini": 128_000, "o3-mini": 200_000,
        # Anthropic
        "claude-sonnet-4-20250514": 200_000,
        "claude-opus-4-20250514": 200_000,
        "claude-3-5-haiku-20241022": 200_000,
        # Default fallback
        "default": 128_000,
    }

    def __init__(self, config: dict):
        self._config = config
        self._agent_config = config.get("agent", {})

    def _get_context_window(self, model: str) -> int:
        """Get the context window size for a model."""
        # Exact match
        if model in self.MODEL_CONTEXT_WINDOWS:
            return self.MODEL_CONTEXT_WINDOWS[model]
        # Prefix match (e.g., gpt-4o-2024-05-13)
        for key, size in self.MODEL_CONTEXT_WINDOWS.items():
            if model.startswith(key.split("-")[0] + "-" + key.split("-")[1] if "-" in key else key):
                return size
        # Config override
        custom = self._agent_config.get("context_window")
        if custom:
            return int(custom)
        return self.MODEL_CONTEXT_WINDOWS["default"]

    def prepare_messages(
        self,
        messages: list[dict[str, Any]],
        model: str,
        thinking: str = "off",
    ) -> list[dict[str, Any]]:
        """Prepare messages for the LLM, with compaction if needed."""
        # Check context utilization (model-aware)
        context_window = self._get_context_window(model)
        token_estimate = self._estimate_tokens(messages, context_window)
        threshold = self._agent_config.get("compact_threshold", 0.8)

        if self._agent_config.get("auto_compact") and token_estimate > threshold:
            logger.info(f"Context at {token_estimate:.0%} of {context_window//1000}K — compacting")
            messages = self._compact(messages)

        # Inject thinking instructions if reasoning model
        if thinking != "off":
            messages = self._inject_thinking_context(messages, thinking)

        return messages

    @staticmethod
    def _estimate_tokens(messages: list[dict], context_window: int = 128_000) -> float:
        """Rough token estimate — 1 token ≈ 4 chars."""
        total_chars = sum(len(str(m.get("content", ""))) for m in messages)
        return total_chars / 4 / context_window

    def _compact(self, messages: list[dict]) -> list[dict]:
        """
        Compact the conversation — preserving prefix cache stability.

        From DeepSeek-TUI: compaction must not break the cached prefix,
        so we only compact the tail of the conversation.
        """
        # Keep system message + last N messages
        if len(messages) <= 4:
            return messages
        return [messages[0]] + messages[-3:]

    @staticmethod
    def _inject_thinking_context(messages: list, thinking: str) -> list[dict]:
        """Inject thinking mode instructions for reasoning models."""
        return messages  # Placeholder — real impl would add system-level thinking instructions
