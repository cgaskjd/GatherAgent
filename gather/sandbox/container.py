"""Container Sandbox — from Hermes-Agent / OpenClaw."""
import asyncio, logging, sys
from pathlib import Path
logger = logging.getLogger(__name__)
class ContainerSandbox:
    BACKENDS = ["docker", "ssh", "modal", "daytona", "singularity"]
    def __init__(self, backend: str = "docker", image: str = "gather-agent-sandbox:latest", workspace: str = "."):
        self._backend = backend; self._image = image; self._workspace = workspace
    def _docker_mount_path(self) -> str:
        """Convert workspace path to Docker-compatible mount format."""
        p = Path(self._workspace).resolve()
        if sys.platform == "win32":
            # Convert G:\path to /g/path for Docker on Windows
            drive = p.drive.rstrip(":").lower()
            return f"/{drive}{p.as_posix()[2:]}"
        return str(p)
    async def execute(self, command: str, timeout: int = 60) -> dict:
        if self._backend == "docker": return await self._docker_exec(command, timeout)
        return {"exit_code": -1, "error": f"Backend {self._backend} not implemented"}
    async def _docker_exec(self, command: str, timeout: int) -> dict:
        mount = self._docker_mount_path()
        cmd = f'docker run --rm -v {mount}:/workspace -w /workspace {self._image} bash -c {repr(command)}'
        proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            return {"exit_code": proc.returncode, "stdout": stdout.decode(), "stderr": stderr.decode()}
        except asyncio.TimeoutError: return {"exit_code": -1, "error": "Timeout"}
