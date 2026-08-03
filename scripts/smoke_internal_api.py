from __future__ import annotations

import json

from opticargo_agents.api import handle_internal_chat
from opticargo_agents.config import load_settings


def main() -> int:
    response = handle_internal_chat(
        {"message": "halo"},
        settings=load_settings({"OPTICARGO_ENVIRONMENT": "development"}),
    )
    print(json.dumps(response, sort_keys=True))
    return 0 if response["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
