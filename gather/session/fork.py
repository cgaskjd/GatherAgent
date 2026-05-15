"""Session Fork — from DeepSeek-TUI."""
import uuid
from gather.session.store import SessionStore
async def fork_session(store: SessionStore, source_id: str, at_turn: int | None = None) -> str:
    messages = await store.load(source_id)
    new_id = str(uuid.uuid4())
    if at_turn is not None: messages = messages[:at_turn * 2]
    await store.save(new_id, messages)
    return new_id
