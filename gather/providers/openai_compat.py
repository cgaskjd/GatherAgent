"""OpenAI-Compatible Provider — supports custom base_url and api_key."""
import os, logging
from gather.providers.base import ModelProvider
logger = logging.getLogger(__name__)
class OpenAICompatProvider(ModelProvider):
    def __init__(self, api_key: str | None = None, base_url: str | None = None, provider_name: str = "openai"):
        self._provider_name = provider_name
        self._api_key = api_key
        self._base_url = base_url
        # If not given, auto-resolve from env or config
        if not self._api_key or not self._base_url:
            self._resolve_defaults()

    def _resolve_defaults(self):
        """Auto-resolve api_key and base_url based on provider name."""
        env_map = {
            "openai": ("OPENAI_API_KEY", None),
            "anthropic": ("ANTHROPIC_API_KEY", None),
            "openrouter": ("OPENROUTER_API_KEY", "https://openrouter.ai/api/v1"),
            "ollama": (None, "http://localhost:11434/v1"),
        }
        key_env, default_url = env_map.get(self._provider_name, (None, None))
        if not self._api_key:
            self._api_key = os.environ.get(key_env) if key_env else None
        if not self._base_url and default_url:
            self._base_url = default_url
        # Try loading from config file
        if not self._api_key or not self._base_url:
            self._load_from_config()

    def _load_from_config(self):
        """Load api_key and base_url from ~/.gather/config.yaml."""
        try:
            from gather.config.loader import load_config
            config = load_config()
            providers_cfg = config.get("providers", {})
            provider_cfg = providers_cfg.get(self._provider_name, {})
            if not self._api_key:
                self._api_key = provider_cfg.get("api_key")
            if not self._base_url:
                self._base_url = provider_cfg.get("base_url")
        except Exception:
            pass

    async def chat(self, model: str, messages: list[dict], tools: list[dict] | None = None, thinking: str = "off", **kwargs) -> dict:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=self._api_key, base_url=self._base_url)
        params = {"model": model, "messages": messages}
        if tools: params["tools"] = [{"type": "function", "function": t} for t in tools]
        response = await client.chat.completions.create(**params)
        msg = response.choices[0].message
        return {"content": msg.content or "", "tool_calls": [tc.model_dump() for tc in (msg.tool_calls or [])],
                "usage": {"input_tokens": response.usage.prompt_tokens, "output_tokens": response.usage.completion_tokens} if response.usage else {}}
    async def stream(self, model: str, messages: list[dict], **kwargs): pass
