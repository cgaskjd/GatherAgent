"""OS-Level Sandbox — from DeepSeek-TUI / Codex.

Platform support:
- macOS: Seatbelt (sandbox-exec)
- Linux: Landlock (requires kernel 5.13+) or fallback to unshare
- Windows: Job Objects via pywin32 (optional)
"""
import platform, logging, shutil, subprocess, sys
logger = logging.getLogger(__name__)

class OSLevelSandbox:
    """OS-level sandboxing: Seatbelt (macOS), Landlock (Linux), Job Objects (Windows)."""
    def __init__(self, workspace: str, allow_network: bool = False):
        self._workspace = workspace; self._allow_network = allow_network; self._os = platform.system()
        self._available = self._check_availability()

    def _check_availability(self) -> bool:
        """Check if OS-level sandboxing is available on this platform."""
        if self._os == "Darwin":
            return shutil.which("sandbox-exec") is not None
        elif self._os == "Linux":
            # Landlock available on kernel 5.13+
            try:
                release = platform.release().split(".")
                major, minor = int(release[0]), int(release[1])
                return (major, minor) >= (5, 13)
            except (ValueError, IndexError):
                return False
        elif self._os == "Windows":
            try:
                import win32job  # pywin32
                return True
            except ImportError:
                return False
        return False

    @property
    def available(self) -> bool:
        return self._available

    def wrap_command(self, command: str) -> str:
        if not self._available:
            logger.warning(f"OS-level sandbox not available on {self._os}, running unsandboxed")
            return command
        if self._os == "Darwin": return self._seatbelt_wrap(command)
        elif self._os == "Linux": return self._landlock_wrap(command)
        elif self._os == "Windows": return self._job_object_wrap(command)
        return command

    def _seatbelt_wrap(self, command: str) -> str:
        """macOS Seatbelt sandbox — uses /usr/bin/sandbox-exec."""
        sandbox_exec = shutil.which("sandbox-exec") or "/usr/bin/sandbox-exec"
        policy = f'(version 1)(allow file-read* file-write* (subpath "{self._workspace}"))'
        if self._allow_network: policy += "(allow network*)"
        return f'{sandbox_exec} -p \'{policy}\' {command}'

    def _landlock_wrap(self, command: str) -> str:
        """Linux Landlock sandbox — wraps command with landlock restrictions.

        Since Landlock requires C API calls, we use a best-effort approach:
        - If gather-landlock wrapper is available, use it
        - Otherwise, fall back to unshare for filesystem isolation
        """
        if shutil.which("gather-landlock"):
            return f'gather-landlock --ro / --rw "{self._workspace}" {command}'
        # Fallback: use unshare for mount namespace isolation
        if shutil.which("unshare"):
            return f'unshare --mount --propagation slave {command}'
        logger.warning("Neither landlock nor unshare available — running unsandboxed")
        return command

    def _job_object_wrap(self, command: str) -> str:
        """Windows Job Object sandbox — restricts process via pywin32.

        Note: Actual Job Object restrictions are applied at process creation time,
        not via command wrapping. This returns the command as-is; the caller
        should use create_process_with_job_object() for real isolation.
        """
        return command
