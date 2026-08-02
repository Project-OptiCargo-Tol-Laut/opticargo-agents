# Open decisions

Keputusan berikut belum boleh ditebak oleh implementation:

- Official repository URLs, release tags, registry, dan checksums untuk Shared/RAG/KG wheels.
- Exact Gateway schema/version dan SSE proxy timeout/reconnect policy.
- Exact ML Models request/response schema version, circuit-breaker policy, dan batch support.
- LangGraph version pin serta policy manual-runner fallback di production.
- LLM provider/model availability, data handling, regional policy, dan readiness requirement.
- Intent heuristic vocabulary, confidence threshold, dan evaluation dataset ownership.
- RAG top-k/min-score and citation coverage threshold per environment.
- Heuristic scoring formula/weights and approval owner.
- Agents OpenAPI exposure pada development/staging.
- Request timeout, concurrency, backpressure, and resource limits.
- Metrics/alert thresholds and dashboard ownership.
- Private vulnerability reporting channel.

Setiap keputusan final dicatat sebagai ADR dan disinkronkan dengan config, tests, Infra, dan runbook.
