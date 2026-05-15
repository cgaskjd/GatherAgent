"""Side-Git Snapshots — from DeepSeek-TUI."""
import subprocess, logging
from pathlib import Path
logger = logging.getLogger(__name__)
class SnapshotManager:
    def __init__(self, workspace: str, snapshot_dir: str = ".gather/snapshots"):
        self._workspace = Path(workspace); self._snapshot_dir = self._workspace / snapshot_dir
    def create_snapshot(self, label: str = "") -> str:
        self._snapshot_dir.mkdir(parents=True, exist_ok=True)
        tag = f"gather-snapshot-{label}" if label else "gather-snapshot"
        try:
            subprocess.run(["git", "add", "-A"], cwd=self._workspace, capture_output=True, timeout=30)
            subprocess.run(["git", "commit", "-m", tag, "--allow-empty"], cwd=self._workspace, capture_output=True, timeout=30)
            return tag
        except Exception as e: logger.warning(f"Snapshot failed: {e}"); return ""
