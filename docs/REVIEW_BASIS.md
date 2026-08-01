# Dasar review

Struktur ini dibuat setelah meninjau:

1. PRD Final Full Product v3.0 OptiCargo.
2. Archive `opticargo-agents-v1.0.0-final-complete` yang dikirimkan.
3. Source package, test, configuration, Docker/build file, workflow, wheel, serta dokumen internal pada archive tersebut.
4. `infra.example.env` yang diberikan sebagai acuan service name, internal URL, command, dan port.

## Bagian archive yang diperiksa

- FastAPI internal endpoints, middleware, lifespan, error handling, health, readiness, dan metrics.
- Settings validation, strict request/response models, typed error, internal authentication, guardrail, logging, dan metrics.
- Conditional workflow state, graph runner, deterministic manual fallback, orchestration service, timeout, concurrency, dan SSE.
- Intent, graph analysis, optimization, retrieval, dan synthesis node.
- ML Models HTTP client serta optional OpenAI-compatible LLM client.
- Knowledge Graph dan RAG adapters.
- Unit/contract/API/client/node/orchestration tests serta opt-in external-stack test.
- Packaging, dependency wheel, Docker, CI, operations, traceability, validation report, dan known limitations.

## Cara menggunakan temuan

Nama file dan responsibilities dipertahankan ketika masih sesuai dengan batas PRD. Detail code tidak disalin. Perilaku yang ditemukan diubah menjadi README, contract, test target, smoke specification, dan open decision. Klaim validasi dari archive lama tidak dianggap sebagai hasil untuk struktur kosong ini.
