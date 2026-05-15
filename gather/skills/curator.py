"""Skill Curator — from Hermes-Agent's lifecycle management."""
import json, logging, time, shutil
from pathlib import Path
logger = logging.getLogger(__name__)
class Curator:
    """Tracks skill lifecycle: active -> stale -> archived."""
    def __init__(self, home: str | None = None, config: dict | None = None):
        self._home = Path(home or "~/.gather").expanduser()
        self._config = config or {}
        self._usage_path = self._home / "skills" / ".usage.json"
        self._archive_path = self._home / "skills" / ".archive"
        self._usage = self._load_usage()
    def _load_usage(self) -> dict:
        if self._usage_path.exists():
            with open(self._usage_path) as f: return json.load(f)
        return {}
    def _save_usage(self):
        self._usage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._usage_path, "w") as f: json.dump(self._usage, f, indent=2)
    def record_use(self, skill_name: str):
        if skill_name not in self._usage: self._usage[skill_name] = {"use_count": 0, "last_activity_at": 0, "state": "active"}
        self._usage[skill_name]["use_count"] += 1
        self._usage[skill_name]["last_activity_at"] = time.time()
        self._save_usage()
    def run_review(self):
        now = time.time(); stale_days = self._config.get("stale_after_days", 30)
        archive_days = self._config.get("archive_after_days", 90)
        for name, info in list(self._usage.items()):
            age_days = (now - info.get("last_activity_at", now)) / 86400
            if info.get("state") == "active" and age_days > stale_days:
                self._usage[name]["state"] = "stale"
            elif info.get("state") == "stale" and age_days > archive_days:
                self._archive(name)
        self._save_usage()
    def _archive(self, name: str):
        self._archive_path.mkdir(parents=True, exist_ok=True)
        src = self._home / "skills" / name
        if src.exists(): shutil.move(str(src), str(self._archive_path / name))
        self._usage[name]["state"] = "archived"
