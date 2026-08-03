#!/usr/bin/env sh
set -eu
python scripts/smoke_env.py
python scripts/smoke_metrics.py
