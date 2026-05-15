"""Audit Trail."""
import json, time, logging
from pathlib import Path
logger = logging.getLogger(__name__)
class AuditTrail:
    def __init__(self, home: str | None = None):
        self._path = Path(home or "~/.gather").expanduser() / "audit.log"
        self._path.parent.mkdir(parents=True, exist_ok=True)
    def record(self, event: str, tool: str, args: dict, result: str | None = None):
        entry = {"timestamp": time.time(), "event": event, "tool": tool, "args": args, "result": result}
        with open(self._path, "a") as f: f.write(json.dumps(entry) + "\n")
