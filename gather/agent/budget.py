"""
Iteration Budget Control — from Hermes-Agent

Three-level budget control:
1. max_iterations: Hard cap on API calls
2. iteration_budget: Token budget for the session
3. grace_call: One final call after budget exhaustion for summarization
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class IterationBudget:
    """
    Three-level iteration budget control.

    From Hermes-Agent's design: prevents agent loops from running forever
    while giving the agent a chance to summarize after budget exhaustion.

    Levels:
    - max_iterations: Absolute cap on the number of LLM API calls
    - token_budget: Optional token-based budget (input + output)
    - grace_call: After budget exhaustion, allow ONE more call for summarization
    """

    def __init__(
        self,
        max_iterations: int = 90,
        token_budget: int | None = None,
        grace_call_enabled: bool = True,
    ):
        self._max_iterations = max_iterations
        self._token_budget = token_budget
        self._grace_call_enabled = grace_call_enabled

        # Tracking
        self._api_call_count = 0
        self._total_input_tokens = 0
        self._total_output_tokens = 0
        self._grace_call_used = False

    def remaining(self) -> bool:
        """Check if the budget has remaining capacity."""
        # Hard cap on iterations
        if self._api_call_count >= self._max_iterations:
            return False

        # Optional token budget
        if self._token_budget is not None:
            total_tokens = self._total_input_tokens + self._total_output_tokens
            if total_tokens >= self._token_budget:
                return False

        return True

    def record_iteration(self, input_tokens: int = 0, output_tokens: int = 0) -> None:
        """Record a completed iteration."""
        self._api_call_count += 1
        self._total_input_tokens += input_tokens
        self._total_output_tokens += output_tokens

    def should_grace_call(self) -> bool:
        """
        Whether a grace call should be performed.

        A grace call is allowed once after budget exhaustion,
        so the agent can produce a meaningful closing summary.
        """
        if not self._grace_call_enabled:
            return False
        if self._grace_call_used:
            return False
        if self.remaining():
            return False  # Budget not exhausted yet, no need for grace call
        return True

    def mark_grace_call_used(self) -> None:
        """Mark that the grace call has been used."""
        self._grace_call_used = True

    @property
    def api_call_count(self) -> int:
        return self._api_call_count

    @property
    def total_tokens(self) -> int:
        return self._total_input_tokens + self._total_output_tokens

    @property
    def utilization_percent(self) -> float:
        """Budget utilization as a percentage (0-100)."""
        if self._token_budget:
            return min(100.0, (self.total_tokens / self._token_budget) * 100)
        return min(100.0, (self._api_call_count / self._max_iterations) * 100)

    def __repr__(self) -> str:
        return (
            f"IterationBudget(calls={self._api_call_count}/{self._max_iterations}, "
            f"tokens={self.total_tokens}/{self._token_budget or '∞'}, "
            f"utilization={self.utilization_percent:.1f}%)"
        )
