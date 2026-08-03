from __future__ import annotations

import json
import os


def main() -> int:
    keys = ["OPTICARGO_ENVIRONMENT", "INTERNAL_SERVICE_TOKEN", "QDRANT_URL", "NEO4J_URI", "ML_MODELS_INTERNAL_URL"]
    print(json.dumps({key: bool(os.getenv(key)) for key in keys}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
