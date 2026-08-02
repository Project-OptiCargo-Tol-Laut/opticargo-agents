# PRD traceability

| PRD requirement | File/module target | Test target |
|---|---|---|
| Intent classification for regulation/matching/route/analytics | `nodes/intent.py`, `orchestrator/graph.py` | unit intent, contract enum, evaluation dataset |
| Conditional routing skips unnecessary nodes | `orchestrator/graph.py`, `state.py` | route golden/parity tests |
| Per-node timeout, retry, circuit/fallback | `nodes/common.py`, clients, service | resilience timeout/retry/fallback |
| Structured recommendation persistable by Gateway | `contracts.py`, `nodes/synthesis.py` | Gateway contract/E2E recommendation |
| Trace/correlation and node latency | API/logging/metrics/trace | API, metrics, integration trace |
| No autonomous booking/payment | guardrails, architecture boundary | architecture/security/E2E human confirmation |
| KG typed discovery/matching/pathfinding context | KG adapter, graph node | package contract and integration |
| RAG citations and abstention | RAG adapter, retrieval/synthesis | citation and abstention evaluation |
| ML scoring with heuristic fallback | ML client, optimization | trained/fallback/resilience tests |
| Health/metrics/internal deployment | API, health, metrics, Docker/Infra | smoke, Prometheus, image gates |
