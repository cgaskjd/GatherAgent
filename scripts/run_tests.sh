#!/usr/bin/env bash
# Hermetic test runner - from Hermes-Agent
set -euo pipefail
unset OPENAI_API_KEY ANTHROPIC_API_KEY OPENROUTER_API_KEY 2>/dev/null || true
export TZ=UTC LANG=C.UTF-8
python -m pytest tests/ -q -n 4 "$@"
