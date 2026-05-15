"""Kanban Board — from Hermes-Agent."""
import sqlite3, json, time, uuid, logging
from pathlib import Path
from enum import Enum
logger = logging.getLogger(__name__)
class TaskState(Enum):
    PENDING = "pending"; CLAIMED = "claimed"; RUNNING = "running"; COMPLETED = "completed"; BLOCKED = "blocked"
class KanbanBoard:
    def __init__(self, db_path: str | None = None):
        self._db_path = str(Path(db_path or "~/.gather/kanban.db").expanduser())
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS tasks (id TEXT PRIMARY KEY, title TEXT, state TEXT, assignee TEXT, created REAL, updated REAL, data TEXT)")
    def create_task(self, title: str, data: dict | None = None) -> str:
        task_id = str(uuid.uuid4())
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("INSERT INTO tasks VALUES (?,?,?,?,?,?,?)", (task_id, title, TaskState.PENDING.value, None, time.time(), time.time(), json.dumps(data or {})))
        return task_id
    def claim_task(self, task_id: str, assignee: str) -> bool:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("UPDATE tasks SET state=?, assignee=?, updated=? WHERE id=?", (TaskState.RUNNING.value, assignee, time.time(), task_id))
        return True
    def complete_task(self, task_id: str) -> bool:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("UPDATE tasks SET state=?, updated=? WHERE id=?", (TaskState.COMPLETED.value, time.time(), task_id))
        return True
