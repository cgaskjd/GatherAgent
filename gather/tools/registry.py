"""Tool Registry — from Hermes-Agent's auto-discovery pattern."""
from __future__ import annotations
import logging
from typing import Any, Callable
logger = logging.getLogger(__name__)

class ToolRegistry:
    """Auto-discovery tool registry. Any gather/tools/*.py with registry.register() is auto-discovered."""
    _instance: ToolRegistry | None = None
    def __init__(self):
        self._tools: dict[str, dict] = {}
        self._toolsets: dict[str, list[str]] = {}
    @classmethod
    def instance(cls) -> ToolRegistry:
        if cls._instance is None: cls._instance = cls()
        return cls._instance
    def register(self, name: str, toolset: str, schema: dict, handler: Callable,
                 check_fn: Callable | None = None, requires_env: list[str] | None = None):
        self._tools[name] = {"name": name, "toolset": toolset, "schema": schema,
                              "handler": handler, "check_fn": check_fn, "requires_env": requires_env or []}
        if toolset not in self._toolsets: self._toolsets[toolset] = []
        if name not in self._toolsets[toolset]: self._toolsets[toolset].append(name)
    def get_handler(self, name: str) -> Callable | None:
        entry = self._tools.get(name)
        return entry["handler"] if entry else None
    def get_schemas_for_model(self, toolsets: list[str] | None = None) -> list[dict]:
        schemas = []
        for name, entry in self._tools.items():
            if entry["check_fn"] and not entry["check_fn"](): continue
            schemas.append(entry["schema"])
        return schemas
    def read_only_tools(self) -> set[str]:
        return {"read_file", "search_files", "list_dir", "git_status", "git_log", "git_diff"}
    def tools_in_toolset(self, toolset: str) -> list[str]: return self._toolsets.get(toolset, [])
    def all_toolsets(self) -> dict[str, list[str]]: return dict(self._toolsets)
    def discover(self):
        """Auto-discover tools in gather/tools/ directory."""
        import importlib, pkgutil, gather.tools as pkg
        for _, name, _ in pkgutil.iter_modules(pkg.__path__):
            try: importlib.import_module(f"gather.tools.{name}")
            except Exception as e: logger.warning(f"Failed to discover tool module {name}: {e}")
