"""OpenRouter Provider."""
import os
from gather.providers.base import ModelProvider
class OpenRouterProvider(ModelProvider):
    def __init__(self, api_key: str | None = None): self._api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
    async def chat(self, model: str, messages: list[dict], tools: list[dict] | None = None, thinking: str = "off", **kwargs) -> dict:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=self._api_key, base_url="https://openrouter.ai/api/v1")
        params = {"model": model, "messages": messages}
        if tools: params["tools"] = [{"type": "function", "function": t} for t in tools]
        response = await client.chat.completions.create(**params)
        msg = response.choices[0].message
        return {"content": msg.content or "", "tool_calls": [], "usage": {}}
    async def stream(self, model: str, messages: list[dict], **kwargs): pass
