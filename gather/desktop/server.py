"""GatherAgent Desktop Backend — FastAPI server for the Electron desktop app.

Provides local HTTP API at port 18790 for the React frontend to communicate
with the Python GatherAgent backend.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logger = logging.getLogger(__name__)

app = FastAPI(title="GatherAgent Desktop API", version="0.1.0")

# Allow Electron/React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global State ──────────────────────────────────────────

_agent = None
_current_model = "gpt-5.5"
_current_provider = "openai"
_custom_base_url: str | None = None
_custom_api_key: str | None = None
_current_mode = "agent"
_sessions: dict[str, dict] = {}


def _get_agent():
    """Lazy init agent."""
    global _agent
    if _agent is None:
        from gather.agent.core import GatherAgent, AgentMode
        mode_map = {
            "plan": AgentMode.PLAN,
            "agent": AgentMode.AGENT,
            "yolo": AgentMode.YOLO,
            "sandbox": AgentMode.SANDBOX,
        }
        _agent = GatherAgent(
            mode=mode_map.get(_current_mode, AgentMode.AGENT),
            model=_current_model,
            provider=_current_provider,
        )
        if _custom_base_url:
            _agent.set_base_url(_custom_base_url)
    return _agent


# ── Request / Response Models ─────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    model: str | None = None
    provider: str | None = None
    base_url: str | None = None
    api_key: str | None = None
    mode: str | None = None


class ChatResponse(BaseModel):
    content: str
    tool_calls: list[dict] | None = None
    usage: dict | None = None
    session_id: str


class ModelSwitchRequest(BaseModel):
    model: str
    provider: str
    base_url: str | None = None
    api_key: str | None = None


class ConfigUpdateRequest(BaseModel):
    model: dict | None = None
    agent: dict | None = None


class SessionCreateRequest(BaseModel):
    title: str | None = None


# ── API Endpoints ─────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    global _agent, _current_model, _current_provider, _custom_base_url, _custom_api_key

    # Apply overrides — reset agent if model/provider changed
    if req.model and req.model != _current_model:
        _current_model = req.model
        _agent = None
    if req.provider and req.provider != _current_provider:
        _current_provider = req.provider
        _agent = None
    if req.base_url:
        _custom_base_url = req.base_url
        _agent = None
    if req.api_key:
        _custom_api_key = req.api_key
        _agent = None
    if req.mode and req.mode != _current_mode:
        global _current_mode
        _current_mode = req.mode
        _agent = None

    agent = _get_agent()
    session_id = req.session_id or str(uuid.uuid4())

    try:
        result = await agent.run(req.message)
        tool_calls = None
        usage = None
        return ChatResponse(
            content=result,
            tool_calls=tool_calls,
            usage=usage,
            session_id=session_id,
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/models")
async def list_models():
    return [
        {"label": "GPT-5.5", "model_id": "gpt-5.5", "provider": "openai"},
        {"label": "GPT-5.5 Pro", "model_id": "gpt-5.5-pro", "provider": "openai"},
        {"label": "GPT-5", "model_id": "gpt-5", "provider": "openai"},
        {"label": "GPT-4o", "model_id": "gpt-4o", "provider": "openai"},
        {"label": "o3-mini", "model_id": "o3-mini", "provider": "openai"},
        {"label": "Claude Opus 4.7", "model_id": "claude-opus-4-7-20260424", "provider": "anthropic"},
        {"label": "Claude Sonnet 4.6", "model_id": "claude-sonnet-4-6-20260205", "provider": "anthropic"},
        {"label": "Claude Haiku 4.5", "model_id": "claude-haiku-4-5-20250514", "provider": "anthropic"},
        {"label": "Gemini 2.5 Pro", "model_id": "google/gemini-2.5-pro", "provider": "openrouter"},
        {"label": "Gemini 3 Pro", "model_id": "google/gemini-3-pro", "provider": "openrouter"},
        {"label": "DeepSeek V4 Pro", "model_id": "deepseek/deepseek-v4-pro", "provider": "openrouter"},
        {"label": "DeepSeek R2", "model_id": "deepseek/deepseek-r2", "provider": "openrouter"},
        {"label": "Llama 4 Maverick", "model_id": "meta-llama/llama-4-maverick", "provider": "openrouter"},
        {"label": "Qwen 3 235B", "model_id": "qwen/qwen-3-235b-a22b", "provider": "openrouter"},
        {"label": "Mistral Large 3", "model_id": "mistralai/mistral-large-3", "provider": "openrouter"},
    ]


@app.post("/api/models/switch")
async def switch_model(req: ModelSwitchRequest):
    global _agent, _current_model, _current_provider, _custom_base_url, _custom_api_key
    _current_model = req.model
    _current_provider = req.provider
    _custom_base_url = req.base_url
    _custom_api_key = req.api_key
    _agent = None  # Force re-init with new settings
    return {"status": "ok", "model": req.model, "provider": req.provider}


@app.get("/api/config")
async def get_config():
    from gather.config.loader import load_config
    config = load_config()
    return {
        "model": {
            "default": _current_model,
            "provider": _current_provider,
            "base_url": _custom_base_url,
            "api_key": "***" if _custom_api_key else None,
        },
        "agent": config.get("agent", {}),
    }


@app.post("/api/config")
async def update_config(req: ConfigUpdateRequest):
    if req.model:
        global _current_model, _current_provider, _custom_base_url, _custom_api_key
        if req.model.get("default"):
            _current_model = req.model["default"]
        if req.model.get("provider"):
            _current_provider = req.model["provider"]
        if req.model.get("base_url"):
            _custom_base_url = req.model["base_url"]
        if req.model.get("api_key"):
            _custom_api_key = req.model["api_key"]
        _agent = None
    return {"status": "ok"}


@app.get("/api/sessions")
async def list_sessions():
    return list(_sessions.values())


@app.post("/api/sessions")
async def create_session(req: SessionCreateRequest | None = None):
    sid = str(uuid.uuid4())
    session = {
        "id": sid,
        "title": (req.title if req else None) or "New Session",
        "created_at": asyncio.get_event_loop().time(),
        "message_count": 0,
    }
    _sessions[sid] = session
    return session


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    _sessions.pop(session_id, None)
    return {"status": "ok"}


def run_server(host: str = "127.0.0.1", port: int = 18790):
    """Start the FastAPI server (blocking)."""
    import uvicorn
    uvicorn.run(app, host=host, port=port, log_level="info")
