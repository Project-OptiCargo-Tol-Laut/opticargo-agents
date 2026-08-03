#!/usr/bin/env sh
set -eu
docker build -f Dockerfile -t ghcr.io/opticargo-ai/opticargo-agents:dev ..
