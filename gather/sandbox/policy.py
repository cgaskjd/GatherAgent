"""Sandbox Policy Engine."""
from dataclasses import dataclass
from enum import Enum
class SandboxMode(Enum):
    AUTO = "auto"; OS = "os"; CONTAINER = "container"; DISABLED = "disabled"
@dataclass
class SandboxPolicy:
    mode: SandboxMode = SandboxMode.AUTO
    allowed_tools: list[str] | None = None
    denied_tools: list[str] | None = None
    allow_network: bool = False
    max_execution_time: int = 300
    def is_tool_allowed(self, tool_name: str) -> bool:
        if self.denied_tools and tool_name in self.denied_tools: return False
        if self.allowed_tools: return tool_name in self.allowed_tools
        return True
