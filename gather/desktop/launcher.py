"""GatherAgent Desktop Launcher — starts Python backend + Electron frontend."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import threading
import time

logger = logging.getLogger(__name__)


def launch_desktop(host: str = "127.0.0.1", port: int = 18790, dev: bool = False):
    """Launch the GatherAgent desktop application.

    1. Start FastAPI backend in a background thread
    2. Wait for backend to be ready
    3. Launch Electron frontend
    """
    # Step 1: Start Python backend
    logger.info(f"Starting GatherAgent backend on {host}:{port}...")
    backend_thread = threading.Thread(
        target=_start_backend,
        args=(host, port),
        daemon=True,
    )
    backend_thread.start()

    # Step 2: Wait for backend
    _wait_for_backend(port, timeout=10)

    # Step 3: Launch frontend
    desktop_dir = _find_desktop_dir()
    if desktop_dir is None:
        logger.error("Desktop directory not found. Run: cd desktop && npm install")
        return

    if dev:
        _launch_dev(desktop_dir)
    else:
        _launch_prod(desktop_dir)


def _start_backend(host: str, port: int):
    """Start the FastAPI backend server."""
    from gather.desktop.server import run_server
    run_server(host=host, port=port)


def _wait_for_backend(port: int, timeout: int = 10):
    """Wait until the backend is responding to health checks."""
    import urllib.request
    import urllib.error

    url = f"http://127.0.0.1:{port}/api/health"
    deadline = time.time() + timeout

    while time.time() < deadline:
        try:
            resp = urllib.request.urlopen(url, timeout=2)
            if resp.status == 200:
                logger.info("Backend is ready.")
                return
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
        time.sleep(0.5)

    logger.warning(f"Backend not ready after {timeout}s, launching frontend anyway...")


def _find_desktop_dir() -> str | None:
    """Find the desktop/ directory."""
    # Check relative to the gather package
    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.path.dirname(pkg_dir)
    desktop_dir = os.path.join(project_root, "desktop")

    if os.path.isfile(os.path.join(desktop_dir, "package.json")):
        return desktop_dir

    return None


def _launch_dev(desktop_dir: str):
    """Launch in dev mode: Vite dev server + Electron."""
    logger.info("Launching in dev mode...")
    # Start Vite dev server
    vite_proc = subprocess.Popen(
        [sys.executable, "-m", "npm", "run", "dev"],
        cwd=desktop_dir,
        shell=True,
    )

    # Give Vite a moment to start
    time.sleep(3)

    # Start Electron
    electron_proc = subprocess.Popen(
        [sys.executable, "-m", "npm", "run", "electron:dev"],
        cwd=desktop_dir,
        shell=True,
    )

    try:
        electron_proc.wait()
    except KeyboardInterrupt:
        pass
    finally:
        vite_proc.terminate()
        electron_proc.terminate()


def _launch_prod(desktop_dir: str):
    """Launch in production mode: serve built files + Electron."""
    # Check if built
    dist_dir = os.path.join(desktop_dir, "dist")
    if not os.path.isdir(dist_dir):
        logger.info("Building frontend first...")
        subprocess.run(
            [sys.executable, "-m", "npm", "run", "build"],
            cwd=desktop_dir,
            shell=True,
            check=True,
        )

    logger.info("Launching Electron...")
    electron_proc = subprocess.Popen(
        [sys.executable, "-m", "npm", "run", "electron:dev"],
        cwd=desktop_dir,
        shell=True,
    )

    try:
        electron_proc.wait()
    except KeyboardInterrupt:
        pass
    finally:
        electron_proc.terminate()
