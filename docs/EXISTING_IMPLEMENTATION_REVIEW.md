# Review implementasi referensi

## Ringkasan

Archive referensi berisi internal FastAPI service dengan endpoint recommendation dan chat SSE, conditional orchestration, typed integration ke Knowledge Graph/RAG, ML scoring, optional LLM, deterministic fallback, health/metrics/logging, package wheel, Dockerfile, dan automated tests.

## Capability yang terlihat

### API dan security

- Entrypoint `opticargo_agents.api:app`.
- `/health/live`, `/health/ready`, `/metrics`.
- `/internal/v1/recommendations` dan `/internal/v1/chat/stream`.
- `X-Internal-Service-Token` memakai constant-time comparison.
- `X-Correlation-ID` diterima atau dibuat lalu diteruskan pada response/dependency call.
- Strict request validation dan safe error envelope.

### Workflow

- Canonical intent: regulation, matching, route, analytics, unknown.
- Request intent lebih dahulu, heuristic classifier berikutnya, optional LLM hanya untuk unknown.
- Matching menjalankan graph analysis, ML/heuristic optimization, optional evidence retrieval, dan synthesis.
- Regulation menjalankan RAG retrieval dan abstain bila evidence tidak cukup.
- Route/analytics menggunakan graph context.
- Compiled LangGraph dan deterministic manual runner dimaksudkan memiliki semantic route yang sama.

### Dependency integration

- Knowledge Graph package menyediakan voyage context, backhaul candidate, route context, dan graph overview.
- RAG package menyediakan hybrid retrieval dan citation metadata.
- ML Models menggunakan internal HTTP readiness dan cargo-match scoring.
- Optional LLM menggunakan OpenAI-compatible API atau disabled client.

### Reliability dan observability

- Global request timeout dan bounded concurrency.
- Bounded ML retry.
- Explicit fallback/abstention.
- Graceful close untuk HTTP/graph/RAG/LLM resources.
- Prometheus metrics untuk request, node, intent, fallback, tool error, recommendation, SSE, citation, dependency, active request, dan build info.
- Structured JSON log dengan correlation ID dan allowlisted context.

## Batas yang harus dipertahankan

- Agents tidak dipanggil browser langsung.
- Agents tidak menjadi source of truth dan tidak mempersist transaksi.
- Agents tidak membuat booking/payment atau mengklaim mutation telah dilakukan.
- Agents tidak menulis Neo4j projection dan tidak melakukan RAG ingestion.
- LLM tidak dapat mengubah hard constraint, model score, identifier, atau citation.
- Error tidak mengekspos secret atau raw dependency response.

## Gap yang tetap membutuhkan bukti pada implementasi baru

- Compatibility dengan official wheels dan exact versions.
- Compiled LangGraph behavior pada dependency version yang dipin.
- Live Gateway-to-Agents recommendation dan SSE proxy.
- Live Neo4j, Qdrant, dan ML Models path.
- Prometheus scrape/Grafana dashboard.
- Fault injection untuk timeout, restart, dependency outage, cancellation, dan backpressure.
- Evaluation set untuk intent, citation, hard constraint, abstention, dan recommendation quality.
- Docker image, non-root runtime, SBOM, checksum, vulnerability scan, dan rollback procedure.

## Keputusan struktur

Struktur source mempertahankan module utama referensi: `api`, `config`, `contracts`, `guardrails`, `health`, `metrics`, `runtime`, `security`, `clients`, `integrations`, `nodes`, `orchestrator`, dan `cli`. Test dipecah lebih jelas menjadi architecture, contract, unit, smoke, integration, E2E, resilience, evaluation, performance, dan security.
