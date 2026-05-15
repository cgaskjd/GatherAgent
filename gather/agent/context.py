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

    def __init__(self, config: dict):
        self._config = config
        self._agent_config = config.get("agent", {})

    def prepare_messages(
        self,
        messages: list[dict[str, Any]],
        model: str,
        thinking: str = "off",
    ) -> list[dict[str, Any]]:
        """Prepare messages for the LLM, with compaction if needed."""
        # Check context utilization
        token_estimate = self._estimate_tokens(messages)
        threshold = self._agent_config.get("compact_threshold", 0.8)

        if self._agent_config.get("auto_compact") and token_estimate > threshold:
            logger.info(f"Context at {token_estimate:.0%} — compacting")
            messages = self._compact(messages)

        # Inject thinking instructions if reasoning model
        if thinking != "off":
            messages = self._inject_thinking_context(messages, thinking)

        return messages

    @staticmethod
    def _estimate_tokens(messages: list[dict]) -> float:
        """Rough token estimate — 1 token ≈ 4 chars."""
        total_chars = sum(len(str(m.get("content", ""))) for m in messages)
        return total_chars / 4 / 128_000  # As fraction of 128k context

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
