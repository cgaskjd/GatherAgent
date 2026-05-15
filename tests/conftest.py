"""Hermetic test environment \u2014 from Hermes-Agent."""
import os, sys, pytest
from pathlib import Path
@pytest.fixture(autouse=True)
def isolate_gather_home(tmp_path, monkeypatch):
    """Redirect GATHER_HOME to temp dir for every test."""
    home = tmp_path / ".gather"; home.mkdir()
    monkeypatch.setenv("GATHER_HOME", str(home))
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "OPENROUTER_API_KEY"]:
        monkeypatch.delenv(key, raising=False)
    # Cross-platform TZ setting
    if sys.platform != "win32":
        monkeypatch.setenv("TZ", "UTC")
    yield home
