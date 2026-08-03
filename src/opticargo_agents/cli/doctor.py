from __future__ import annotations

import json

from opticargo_agents.config import get_settings
from opticargo_agents.health import liveness_report, readiness_report


def main() -> int:
    settings = get_settings()
    payload = {
        "service": "opticargo-agents",
        "environment": settings.environment,
        "liveness": liveness_report(),
        "readiness": readiness_report().to_dict(),
    }
    print(json.dumps(payload, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["main"]
