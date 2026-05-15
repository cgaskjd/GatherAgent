"""Skill Loader — from Hermes-Agent's discovery + DeepSeek-TUI's multi-path scan."""
import logging
from pathlib import Path
from dataclasses import dataclass
logger = logging.getLogger(__name__)
@dataclass
class Skill:
    name: str; description: str; version: str = "1.0"; author: str = ""; platforms: list[str] | None = None; content: str = ""
class SkillLoader:
    DISCOVERY_PATHS = [".agents/skills", "skills", ".opencode/skills", ".claude/skills", ".cursor/skills"]
    def __init__(self, home: str | None = None):
        self._home = Path(home or "~/.gather").expanduser(); self._skills: dict[str, Skill] = {}
    def discover(self):
        for base in self.DISCOVERY_PATHS:
            skill_dir = self._home / base
            if skill_dir.exists():
                for d in skill_dir.iterdir():
                    if d.is_dir() and (d / "SKILL.md").exists(): self._load_skill(d)
        logger.info(f"Discovered {len(self._skills)} skills")
        return self._skills
    def _load_skill(self, path: Path):
        content = (path / "SKILL.md").read_text(encoding="utf-8")
        name = path.name; desc = ""
        for line in content.split("\n"):
            if line.startswith("description:"): desc = line.split(":", 1)[1].strip(); break
        self._skills[name] = Skill(name=name, description=desc, content=content)
    def get(self, name: str) -> Skill | None: return self._skills.get(name)
    def list_skills(self) -> list[Skill]: return list(self._skills.values())
