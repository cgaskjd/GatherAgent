"""Session Store — SQLite + FTS5 from Hermes-Agent, fork from DeepSeek-TUI."""
import sqlite3, json, logging, time
from pathlib import Path
logger = logging.getLogger(__name__)
class SessionStore:
    def __init__(self, home: str | None = None):
        self._db_path = str(Path(home or "~/.gather").expanduser() / "sessions.db")
        self._init_db()
    def _init_db(self):
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, created REAL, messages TEXT)")
    async def save(self, session_id: str, messages: list[dict]):
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("INSERT OR REPLACE INTO sessions VALUES (?,?,?)", (session_id, time.time(), json.dumps(messages)))
    async def load(self, session_id: str) -> list[dict]:
        with sqlite3.connect(self._db_path) as conn:
            row = conn.execute("SELECT messages FROM sessions WHERE id=?", (session_id,)).fetchone()
            return json.loads(row[0]) if row else []
