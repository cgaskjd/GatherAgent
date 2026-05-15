"""Shell command execution tool."""
import subprocess, json, sys, shutil
from gather.tools.registry import registry

def _detect_shell() -> list[str]:
    """Detect the best available shell for the current platform."""
    if sys.platform == "win32":
        # Prefer PowerShell, fall back to cmd
        if shutil.which("powershell"): return ["powershell", "-Command"]
        if shutil.which("pwsh"): return ["pwsh", "-Command"]
        return ["cmd", "/c"]
    else:
        # macOS / Linux — prefer bash, fall back to sh
        if shutil.which("bash"): return ["bash", "-c"]
        return ["sh", "-c"]

def _run_shell(command: str, cwd: str | None = None, timeout: int = 60, **kw) -> str:
    try:
        shell_cmd = _detect_shell() + [command]
        result = subprocess.run(shell_cmd, capture_output=True, text=True, cwd=cwd, timeout=timeout)
        return json.dumps({"exit_code": result.returncode, "stdout": result.stdout[:10000], "stderr": result.stderr[:5000]})
    except subprocess.TimeoutExpired: return json.dumps({"exit_code": -1, "error": f"Timeout after {timeout}s"})
    except Exception as e: return json.dumps({"exit_code": -1, "error": str(e)})
registry.register(name="shell", toolset="core", handler=lambda args, **kw: _run_shell(**args),
    schema={"name": "shell", "description": "Execute a shell command", "parameters": {
        "type": "object", "properties": {"command": {"type": "string"}, "cwd": {"type": "string"}, "timeout": {"type": "integer", "default": 60}},
        "required": ["command"]}})
