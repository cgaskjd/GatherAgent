"""Approval Gate — from Claude-Code."""
import logging
from dataclasses import dataclass
from enum import Enum
logger = logging.getLogger(__name__)
class ApprovalDecision(Enum):
    APPROVE = "approve"; DENY = "deny"; ALWAYS_APPROVE = "always_approve"
@dataclass
class ApprovalRequest:
    tool_name: str; arguments: dict; risk_level: str = "medium"
class ApprovalGate:
    HIGH_RISK_TOOLS = {"shell", "write_file", "edit_file", "delete_file"}
    def __init__(self, mode: str = "agent"): self._mode = mode; self._always_approved: set[str] = set()
    async def check(self, request: ApprovalRequest) -> ApprovalDecision:
        if self._mode == "yolo": return ApprovalDecision.APPROVE
        if request.tool_name in self._always_approved: return ApprovalDecision.APPROVE
        if request.tool_name in self.HIGH_RISK_TOOLS: return ApprovalDecision.DENY
        return ApprovalDecision.APPROVE
    def always_approve(self, tool_name: str): self._always_approved.add(tool_name)
