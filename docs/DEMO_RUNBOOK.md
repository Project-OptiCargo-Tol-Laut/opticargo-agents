# Demo runbook

## Goal

Membuktikan regulation dan matching critical paths tanpa manual database edit atau hardcoded final response.

## Preflight

- Immutable image tags and release metadata recorded.
- Gateway, Agents, ML Models, Neo4j, Qdrant, and required stores ready.
- Deterministic dataset/index/projection versions recorded.
- Internal token and dependency secret injected.
- Prometheus scrape and dashboard healthy.
- Backup video/fallback path prepared.

## Scenario 1 — Regulation

1. Submit regulation query through frontend/Gateway.
2. Verify Gateway-to-Agents trace ID.
3. Observe SSE meta/status/citation/token/done.
4. Verify real citation and active document version.
5. Run no-evidence query and verify abstention.

## Scenario 2 — Matching

1. Open seeded voyage.
2. Request recommendation through Gateway.
3. Verify graph route, candidate hard filters, trained or declared fallback model mode, score breakdown, and alternatives.
4. Verify invalid candidate is absent.
5. Verify response requests human confirmation and does not create booking/payment.

## Failure demonstration

Temporarily disable ML Models in controlled environment and verify heuristic fallback flag/metric. Restore service and verify readiness/recovery.
