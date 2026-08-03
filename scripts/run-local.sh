#!/usr/bin/env sh
set -eu
uvicorn opticargo_agents.api:app --host 0.0.0.0 --port 8000
