"""Anthropic Provider."""
import os
from gather.providers.base import ModelProvider
class AnthropicProvider(ModelProvider):
    def __init__(self, api_key: str | None = None): self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    async def chat(self, model: str, messages: list[dict], tools: list[dict] | None = None, thinking: str = "off", **kwargs) -> dict:
        from anthropic import AsyncAnthropic
        client = AsyncAnthropic(api_key=self._api_key)
        params = {"model": model, "messages": messages, "max_tokens": 4096}
        if thinking != "off": params["thinking"] = {"type": "enabled", "budget_tokens": 10000 if thinking == "high" else 32000}
        response = await client.messages.create(**params)
        return {"content": response.content[0].text if response.content else "", "tool_calls": [],
                "usage": {"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens}}
    async def stream(self, model: str, messages: list[dict], **kwargs): pass
