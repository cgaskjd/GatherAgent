"""User Modeling — from Hermes-Agent's Honcho integration."""
import json, logging
from pathlib import Path
logger = logging.getLogger(__name__)
class UserModel:
    """Dialectic user modeling — understands user preferences across sessions."""
    def __init__(self, home: str | None = None):
        self._path = Path(home or "~/.gather").expanduser() / "user_model.json"
        self._model = self._load()
    def _load(self) -> dict:
        if self._path.exists():
            with open(self._path) as f: return json.load(f)
        return {"preferences": {}, "style": {}, "frequent_tasks": []}
    def save(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w") as f: json.dump(self._model, f, indent=2)
    def update_preference(self, key: str, value: str): self._model["preferences"][key] = value; self.save()
    def get_preference(self, key: str, default: str = "") -> str: return self._model["preferences"].get(key, default)
    def get_context_for_prompt(self) -> str:
        prefs = "\n".join(f"- {k}: {v}" for k, v in self._model["preferences"].items())
        return f"User preferences:\n{prefs}" if prefs else ""
