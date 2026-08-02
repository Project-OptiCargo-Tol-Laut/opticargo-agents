# OptiCargo Agents

Repository ini menyediakan **struktur awal implementasi** untuk service orkestrasi internal OptiCargo Agents. Seluruh file source, test, script, build configuration, dan workflow masih kosong. Penjelasan fungsi, contract, dependency, alur runtime, serta pengujian disimpan pada README di setiap folder dan dokumen pada `docs/`.

## Peran repository

Agents menghasilkan satu internal service dan satu installable Python package yang mengatur:

1. intent routing untuk `regulation`, `matching`, `route`, `analytics`, dan `unknown`;
2. conditional workflow melalui node graph analysis, retrieval, optimization, dan synthesis;
3. integrasi typed package Knowledge Graph serta RAG;
4. pemanggilan internal ML Models untuk cargo-match scoring;
5. deterministic fallback dan explicit abstention;
6. structured recommendation yang dapat dipersist oleh Gateway;
7. SSE chat stream, correlation ID, health, readiness, metrics, dan structured logs.

Service ini **tidak memiliki public ingress**. Browser hanya berkomunikasi dengan `opticargo-gateway-api`. Agents tidak membuat booking, tidak mengubah payment, tidak menjadi source of truth transaksi, tidak menulis projection Neo4j, dan tidak mengindeks dokumen ke Qdrant.

## Alur runtime

```text
Browser
  │
  ▼
opticargo-gateway-api
  │ authenticated internal request + correlation ID
  ▼
opticargo-agents
  ├── intent classification
  ├── Knowledge Graph package ──► Neo4j projection
  ├── RAG package ──────────────► Qdrant index
  ├── ML Models HTTP ───────────► cargo-match scoring
  ├── guarded synthesis
  └── structured JSON / SSE response
        │
        ▼
Gateway persistence, audit, booking/payment confirmation, dan delivery ke browser
```

## Conditional workflow

```text
intent
  ├── regulation ─► retrieval ─────────────────────► synthesis
  ├── matching   ─► graph analysis ─► optimization ─► retrieval ─► synthesis
  ├── route      ─► graph analysis ─► retrieval ────► synthesis
  ├── analytics  ─► graph analysis ─────────────────► synthesis
  └── unknown    ───────────────────────────────────► clarification
```

## Struktur repository

| Path | Kegunaan |
|---|---|
| `src/opticargo_agents/` | API internal, runtime composition, workflow, node, adapters, client, contracts, guardrail, health, metrics, logging, dan CLI. |
| `tests/` | Architecture, contract, unit, smoke, integration, E2E, resilience, evaluation, performance, dan security tests. |
| `docs/` | Arsitektur, API, workflow, node behavior, integration contract, fallback, security, operations, testing, Infra, dependency wheel, ADR, dan Definition of Done. |
| `config/` | Acuan environment Infra serta daftar konfigurasi khusus Agents. |
| `scripts/` | Placeholder bootstrap, validation, smoke, dependency wheel, local run, image build, dan demo preflight. |
| `.github/` | Template issue/PR, CODEOWNERS template, dan workflow yang masih dinonaktifkan. |
| `vendor/` | Lokasi opsional wheel immutable `opticargo-shared`, `opticargo-rag-pipeline`, dan `opticargo-knowledge-graph` untuk mode offline. |

## Status struktur awal

- Semua file Python pada `src/` dan `tests/` belum berisi kode.
- Semua script, `pyproject.toml`, requirements, Dockerfile, Makefile, Compose overlay, dan workflow belum berisi konfigurasi aktif.
- Tidak ada test runtime yang diklaim lulus.
- Tidak ada wheel, image, atau generated artifact yang dibundel.
- Port internal service mengikuti kontrak Infra `agents:8000`; tidak ada host/public port baru yang ditetapkan.

## Dokumen awal yang perlu dibaca

1. [`docs/00_START_HERE.md`](docs/00_START_HERE.md)
2. [`docs/EXISTING_IMPLEMENTATION_REVIEW.md`](docs/EXISTING_IMPLEMENTATION_REVIEW.md)
3. [`docs/ARCHITECTURE_TARGET.md`](docs/ARCHITECTURE_TARGET.md)
4. [`docs/INTERNAL_API_CONTRACT.md`](docs/INTERNAL_API_CONTRACT.md)
5. [`docs/WORKFLOW_ROUTING.md`](docs/WORKFLOW_ROUTING.md)
6. [`docs/NODE_BEHAVIOR.md`](docs/NODE_BEHAVIOR.md)
7. [`docs/INTEGRATION_CONTRACTS.md`](docs/INTEGRATION_CONTRACTS.md)
8. [`docs/FALLBACK_AND_ABSTENTION.md`](docs/FALLBACK_AND_ABSTENTION.md)
9. [`docs/TESTING_STRATEGY.md`](docs/TESTING_STRATEGY.md)
10. [`docs/DEFINITION_OF_DONE.md`](docs/DEFINITION_OF_DONE.md)

## Prinsip implementasi

- Gunakan contract `opticargo-shared==1.0.0`; jangan mendefinisikan ulang enum atau schema lintas repository tanpa versioning.
- Install RAG dan Knowledge Graph sebagai release wheel; jangan melakukan import dari sibling source path.
- Gateway tetap owner autentikasi pengguna, otorisasi bisnis, transaksi, audit, dan persistence recommendation.
- Hard constraint harus diverifikasi sebelum ranking dan tidak boleh dioverride oleh LLM.
- Respons regulasi harus memiliki evidence/citation atau abstain; sumber tidak boleh dibuat-buat.
- Failure ML menggunakan heuristic fallback yang ditandai eksplisit, bukan silent substitution.
- Failure Knowledge Graph pada matching/route dan failure RAG pada regulation menghasilkan typed abstention.
- Booking dan payment selalu membutuhkan konfirmasi manusia melalui Gateway/frontend.
- Internal token, API key, full evidence document, credential, dan raw dependency response tidak boleh masuk log atau SSE error.
- Correlation ID, timeout, bounded concurrency, retry terbatas, health, metrics, dan graceful shutdown dirancang sejak awal.

## Referensi file

- [`docs/SOURCE_FILE_CATALOG.md`](docs/SOURCE_FILE_CATALOG.md): tanggung jawab seluruh file source.
- [`docs/TEST_FILE_CATALOG.md`](docs/TEST_FILE_CATALOG.md): tujuan seluruh file test.
- [`FILE_MANIFEST.md`](FILE_MANIFEST.md): daftar file struktur awal.
- [`REPOSITORY_INITIALIZATION_POLICY.md`](REPOSITORY_INITIALIZATION_POLICY.md): batas perubahan sebelum implementasi dimulai.
