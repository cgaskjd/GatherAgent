"""Simple file-based memory provider."""
import json, os
from pathlib import Path
from gather.memory.provider import MemoryProvider
class SimpleMemoryProvider(MemoryProvider):
    def __init__(self, store_path: str | None = None):
        self._path = Path(store_path or "~/.gather/memory").expanduser()
        self._path.mkdir(parents=True, exist_ok=True)
    def store(self, key: str, value: str, metadata: dict | None = None) -> str:
        entry = {"key": key, "value": value, "metadata": metadata or {}}
        with open(self._path / f"{key}.json", "w") as f: json.dump(entry, f)
        return json.dumps({"status": "stored", "key": key})
    def recall(self, query: str, limit: int = 5) -> list[dict]:
        results = []
        for f in sorted(self._path.glob("*.json"))[:limit]:
            with open(f) as fh: results.append(json.load(fh))
        return results
    def search(self, query: str, limit: int = 10) -> list[dict]: return self.recall(query, limit)
    def sync_turn(self, turn_messages: list[dict]) -> None: pass
    def shutdown(self) -> None: pass
