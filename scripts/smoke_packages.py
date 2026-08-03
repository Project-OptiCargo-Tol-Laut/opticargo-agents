from __future__ import annotations

import json

from opticargo_agents.runtime import build_runtime


def main() -> int:
    runtime = build_runtime()
    payload = {
        "agents_port": runtime.settings.port,
        "rag_health": runtime.rag.health()["status"],
        "knowledge_graph_health": runtime.knowledge_graph.health()["status"],
        "ml_models_health": runtime.ml_models.health()["status"],
    }
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
