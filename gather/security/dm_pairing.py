"""DM Pairing — from OpenClaw."""
import random, string, json, logging
from pathlib import Path
logger = logging.getLogger(__name__)
class DMPairing:
    def __init__(self, home: str | None = None):
        self._path = Path(home or "~/.gather").expanduser() / "paired_senders.json"
        self._paired = self._load()
    def _load(self) -> set:
        if self._path.exists():
            with open(self._path) as f: return set(json.load(f))
        return set()
    def _save(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w") as f: json.dump(list(self._paired), f)
    def generate_code(self) -> str: return "".join(random.choices(string.digits, k=6))
    def is_paired(self, sender: str) -> bool: return sender in self._paired
    def approve(self, sender: str): self._paired.add(sender); self._save()
