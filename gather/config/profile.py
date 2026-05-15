"""Profile Multi-Instance — from Hermes-Agent."""
import os
from pathlib import Path
from gather.config.loader import set_gather_home
def apply_profile(profile: str | None = None):
    if profile:
        home = Path.home() / ".gather" / "profiles" / profile
        home.mkdir(parents=True, exist_ok=True)
        os.environ["GATHER_HOME"] = str(home)
        set_gather_home(home)
