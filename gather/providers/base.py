"""Model Provider ABC."""
from abc import ABC, abstractmethod
from typing import Any
class ModelProvider(ABC):
    @abstractmethod
    async def chat(self, model: str, messages: list[dict], tools: list[dict] | None = None, thinking: str = "off", **kwargs) -> dict: ...
    @abstractmethod
    async def stream(self, model: str, messages: list[dict], **kwargs) -> Any: ...
