# Smoke test specification

## Level 0 — Repository structure

Memastikan source/test/script/build placeholders dan README/catalog konsisten; tidak ada implementation code atau active workflow pada initial commit.

## Level 1 — Package build

- Build wheel.
- Install pada clean environment.
- Verify distribution/version/typed marker.
- Import package dan `create_app` tanpa eager network.

## Level 2 — Dependency wheels

Memverifikasi distribution name, version, checksum, import, dan minimum symbol dari Shared, RAG, dan Knowledge Graph.

## Level 3 — Configuration

Memvalidasi required keys, secret policy, URL/scheme/range, package versions, and production-like restrictions.

## Level 4 — Process

- Start internal service.
- `/health/live` 200.
- `/health/ready` sesuai dependency state.
- `/metrics` Prometheus-valid.
- Route inventory hanya health/metrics/internal endpoints.

## Level 5 — Internal API

- Unauthorized negative case.
- Recommendation request dengan deterministic fixture.
- Chat SSE `meta` first and one terminal event.
- Correlation ID propagation.

## Level 6 — Live dependency

- KG query.
- RAG retrieval/citation.
- ML scoring trained/fallback.
- Optional LLM policy.

## Level 7 — Failure/recovery

- Dependency outage.
- Timeout/cancellation.
- Retry then success.
- Restart recovery.
- Concurrency saturation.

## Level 8 — Gateway/staging

Gateway call/proxy, Prometheus scrape, dashboard, alerts, image tag, rollback, and demo preflight.
