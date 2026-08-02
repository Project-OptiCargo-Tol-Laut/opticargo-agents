# Testing strategy

## Layer

| Layer | Tujuan |
|---|---|
| Architecture | Dependency direction, internal-only service, no mutation, no source-path imports. |
| Contract | Gateway, SSE, health, metrics, Shared/RAG/KG/ML schema/version. |
| Unit | Config, contracts, guardrail, clients, adapters, nodes, state, graph, service. |
| Smoke | Install/import/startup/routes/readiness/metrics/dependency connectivity. |
| Integration | Compiled LangGraph, live KG/RAG/ML, Gateway proxy, Prometheus, shutdown. |
| E2E | Matching, regulation, route, analytics, unknown, no-match, human confirmation. |
| Resilience | Timeout, retry, outage, restart, invalid response, cancellation, saturation. |
| Evaluation | Intent, hard constraint, citation, abstention, fallback, output quality. |
| Performance | p95 request/node, time-to-first-event, concurrency/backpressure. |
| Security | Internal auth, redaction, route exposure, prompt boundary, no credential/mutation. |

## Mandatory demo dataset

- Matching voyage dengan beberapa candidate valid dan satu hard-constraint invalid.
- No-match scenario.
- Regulation query dengan valid versioned citations.
- Regulation query tanpa evidence untuk abstention.
- Route and analytics queries.
- ML trained response dan ML outage heuristic fallback.
- LLM disabled/unavailable deterministic result.

## Gate

Unit/contract/architecture wajib lulus sebelum integration. Integration wajib lulus sebelum E2E. Evaluation/performance/security threshold harus tercatat sebelum release freeze.
