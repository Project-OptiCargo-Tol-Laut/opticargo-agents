from __future__ import annotations

import json

from opticargo_agents.api import app_routes
from opticargo_agents.orchestrator import WORKFLOW_ROUTES
from opticargo_agents.version import __version__


def main() -> int:
    payload = {
        "package": "opticargo-agents",
        "version": __version__,
        "routes": app_routes(),
        "workflow_intents": sorted(WORKFLOW_ROUTES),
    }
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
