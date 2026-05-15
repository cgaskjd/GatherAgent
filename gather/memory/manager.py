"""Memory Manager — orchestrates pluggable memory providers."""
from __future__ import annotations
import logging
from gather.memory.provider import MemoryProvider
logger = logging.getLogger(__name__)
class MemoryManager:
    def __init__(self, provider: MemoryProvider, config: dict):
        self._provider = provider; self._config = config
    def store(self, key: str, value: str, metadata: dict | None = None) -> str: return self._provider.store(key, value, metadata)
    def recall(self, query: str, limit: int = 5) -> list[dict]: return self._provider.recall(query, limit)
    def sync_turn(self, messages: list[dict]) -> None: self._provider.sync_turn(messages)
    def shutdown(self) -> None: self._provider.shutdown()
