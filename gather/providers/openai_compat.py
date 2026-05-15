"""OpenAI-Compatible Provider."""
import os, logging
from gather.providers.base import ModelProvider
logger = logging.getLogger(__name__)
class OpenAICompatProvider(ModelProvider):
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY"); self._base_url = base_url
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
