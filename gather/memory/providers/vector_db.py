"""Vector DB memory provider — from OpenClaw's LanceDB pattern."""
import json
from gather.memory.provider import MemoryProvider
class VectorDBMemoryProvider(MemoryProvider):
    def __init__(self, **kwargs): self._store = []
    def store(self, key: str, value: str, metadata: dict | None = None) -> str:
        self._store.append({"key": key, "value": value}); return json.dumps({"status": "stored"})
    def recall(self, query: str, limit: int = 5) -> list[dict]: return self._store[:limit]
    def search(self, query: str, limit: int = 10) -> list[dict]: return self._store[:limit]
    def sync_turn(self, turn_messages: list[dict]) -> None: pass
    def shutdown(self) -> None: pass
