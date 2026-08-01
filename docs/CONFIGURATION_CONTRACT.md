# Configuration contract

## Kelompok

- identity/release;
- internal authentication;
- Agents host/port/timeout/concurrency/top-N/OpenAPI policy;
- ML Models URL/timeout/retry;
- Neo4j and graph query settings;
- Qdrant/RAG retrieval settings;
- optional LLM provider settings;
- heuristic fallback defaults;
- readiness policy;
- logging/correlation settings.

## Validation

- Secret wajib tidak kosong pada staging/production-like environment.
- URL HTTP memakai `http/https`; Neo4j memakai supported Bolt/Neo4j scheme.
- Timeout, retry, top-N, temperature, token, score, radius, tolerance, dan concurrency memiliki range aman.
- Shared/RAG/KG package version harus cocok dengan release contract.
- Production-like environment tidak menerima `dev-only-*` value.
- OpenAPI exposure mengikuti internal environment policy.

## Change rule

Penambahan key membutuhkan Settings field, docs, env example, Infra manifest, validation test, smoke test, dan backwards-compatible default atau migration note.
