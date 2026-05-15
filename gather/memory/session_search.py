"""FTS5 Session Search — from Hermes-Agent."""
import sqlite3, json, logging, time, uuid
from pathlib import Path
logger = logging.getLogger(__name__)
class SessionSearch:
    def __init__(self, db_path: str | None = None):
        self._db_path = str(Path(db_path or "~/.gather/sessions.db").expanduser())
        self._init_db()
    def _init_db(self):
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS messages (id TEXT, session_id TEXT, role TEXT, content TEXT, timestamp REAL)")
    def index_message(self, session_id: str, role: str, content: str):
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("INSERT INTO messages VALUES (?,?,?,?,?)", (str(uuid.uuid4()), session_id, role, content, time.time()))
    def search(self, query: str, limit: int = 10) -> list[dict]:
        with sqlite3.connect(self._db_path) as conn:
            rows = conn.execute("SELECT session_id, role, content FROM messages WHERE content LIKE ? LIMIT ?", (f"%{query}%", limit)).fetchall()
            return [{"session_id": r[0], "role": r[1], "content": r[2]} for r in rows]
