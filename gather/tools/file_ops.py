"""File operations tools."""
import os, json
from gather.tools.registry import registry
def _read_file(path: str, **kw) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f: return f.read()
    except Exception as e: return json.dumps({"error": str(e)})
def _write_file(path: str, content: str, **kw) -> str:
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f: f.write(content)
        return json.dumps({"success": True, "path": path})
    except Exception as e: return json.dumps({"error": str(e)})
def _search_files(pattern: str, path: str = ".", **kw) -> str:
    """Search files — tries rg, falls back to grep, then to Python glob."""
    import subprocess, shutil
    try:
        # Try ripgrep first (fastest)
        if shutil.which("rg"):
            r = subprocess.run(["rg", "-l", pattern, path], capture_output=True, text=True, timeout=30)
            return json.dumps({"files": r.stdout.strip().split("\n") if r.stdout.strip() else []})
        # Fall back to grep (available on Linux/macOS, Git Bash on Windows)
        if shutil.which("grep"):
            r = subprocess.run(["grep", "-rl", pattern, path], capture_output=True, text=True, timeout=30)
            return json.dumps({"files": r.stdout.strip().split("\n") if r.stdout.strip() else []})
        # Final fallback: Python native glob
        import fnmatch
        from pathlib import Path as P
        matches = [str(p) for p in P(path).rglob("*") if fnmatch.fnmatch(p.name, f"*{pattern}*")]
        return json.dumps({"files": matches[:100]})
    except Exception as e: return json.dumps({"error": str(e)})
registry.register("read_file", "core", handler=lambda args, **kw: _read_file(**args),
    schema={"name": "read_file", "description": "Read a file", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}})
registry.register("write_file", "core", handler=lambda args, **kw: _write_file(**args),
    schema={"name": "write_file", "description": "Write content to a file", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}})
registry.register("search_files", "core", handler=lambda args, **kw: _search_files(**args),
    schema={"name": "search_files", "description": "Search files by pattern", "parameters": {"type": "object", "properties": {"pattern": {"type": "string"}, "path": {"type": "string"}}, "required": ["pattern"]}})
