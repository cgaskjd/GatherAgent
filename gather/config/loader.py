"""Config Loader — from Hermes-Agent's multi-layer pattern."""
import os, yaml, logging
from pathlib import Path
logger = logging.getLogger(__name__)
_GATHER_HOME: Path | None = None
DEFAULT_CONFIG = {
    "model": {"default": "gpt-4o", "provider": "openai", "thinking": "off", "auto_mode": False},
    "agent": {"max_iterations": 90, "mode": "agent", "grace_call": True},
    "memory": {"provider": "simple", "session_search": True},
    "sandbox": {"mode": "auto"},
    "session": {"storage": "sqlite", "side_git_snapshots": True},
    "tui": {"theme": "default", "locale": "auto"},
}
def get_gather_home() -> Path:
    global _GATHER_HOME
    if _GATHER_HOME: return _GATHER_HOME
    env = os.environ.get("GATHER_HOME")
    _GATHER_HOME = Path(env) if env else Path.home() / ".gather"
    return _GATHER_HOME
def set_gather_home(path: Path):
    global _GATHER_HOME; _GATHER_HOME = path
def load_config(profile: str | None = None) -> dict:
    home = get_gather_home()
    if profile: home = home / "profiles" / profile
    config = dict(DEFAULT_CONFIG)
    config_path = home / "config.yaml"
    if config_path.exists():
        with open(config_path) as f: user_config = yaml.safe_load(f) or {}
        config = _deep_merge(config, user_config)
    return config
def _deep_merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict): result[k] = _deep_merge(result[k], v)
        else: result[k] = v
    return result
