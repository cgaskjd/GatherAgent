#!/usr/bin/env bash
set -euo pipefail

echo "Installing GatherAgent..."

# Check Python version (requires 3.11+)
if ! command -v python3 &>/dev/null; then
    echo "Error: Python 3.11+ is required but not found."
    echo "Install: https://www.python.org/downloads/"
    exit 1
fi

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

if [ "$PY_MAJOR" -lt 3 ] || ([ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 11 ]); then
    echo "Error: Python 3.11+ required, found $PY_VERSION"
    exit 1
fi

echo "Python $PY_VERSION found ✓"

# Check optional system deps
for cmd in git rg; do
    if command -v "$cmd" &>/dev/null; then
        echo "$cmd found ✓"
    else
        echo "$cmd not found (optional — some features may be limited)"
    fi
done

pip install -e ".[all]"
gather doctor
echo "Done! Run: gather"
