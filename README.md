# OptiCargo Agents

`opticargo-agents` adalah orchestrator LangGraph untuk asisten logistik maritim OptiCargo. Layanan ini menerima pertanyaan pengguna, menentukan intent, mengumpulkan evidence dari Knowledge Graph dan RAG, menjalankan optimasi kandidat muatan bila diperlukan, lalu mengembalikan rekomendasi beserta citation.

## Kemampuan utama

- Endpoint HTTP `POST /recommend` untuk menjalankan graph agent end-to-end.
- Klasifikasi intent: `REGULATION_QUERY`, `ROUTE_OPTIMIZATION`, `GENERAL_CHAT`, dan `OUT_OF_SCOPE`.
- Self-correction Cypher: membangun query, memvalidasi dengan `EXPLAIN`, lalu mengeksekusi query valid pada Neo4j.
- Pencarian kandidat backhaul dan scoring melalui `opticargo-ml-models` dengan fallback heuristic lokal.
- Retrieval regulasi melalui `opticargo-rag-pipeline` dan penyusunan citation pada respons akhir.
- Narasi rekomendasi dengan LLM ketika credential tersedia, dengan fallback yang terstruktur ketika tidak tersedia.

## Arsitektur alur keputusan

```mermaid
flowchart LR
    Request["POST /recommend"] --> Intent["Intent extraction"]
    Intent -->|"REGULATION_QUERY"| RAG["RAG retrieval"]
    Intent -->|"ROUTE_OPTIMIZATION"| Graph["Graph analysis"]
    Graph --> Validate["Cypher EXPLAIN / repair"]
    Validate --> Execute["Neo4j query execution"]
    Execute --> Optimize["ML cargo-match scoring"]
    Optimize --> RAG
    Intent -->|"GENERAL_CHAT / OUT_OF_SCOPE"| Recommend["Recommendation"]
    RAG --> Recommend
    Recommend --> Response["Summary, citation, confidence"]
```

## API

### `POST /recommend`

Contoh request:

```json
{
  "query": "Carikan peluang muatan balik dari Natuna dengan kapasitas minimal 20 ton",
  "voyage_id": "<uuid-voyage-opsional>",
  "correlation_id": "<uuid-opsional>"
}
```

Respons sukses mengikuti kontrak `RecommendResponse` dari `opticargo-shared`: ringkasan, intent, citation, confidence, status fallback, dan warning.

Endpoint operasional:

| Endpoint | Kegunaan |
|---|---|
| `GET /health` | Health check layanan. |
| `GET /health/live` | Liveness probe. |
| `GET /health/ready` | Readiness probe. |
| `GET /metrics` | Metrik Prometheus dasar. |

## Integrasi antar-repository

| Dependency | Peran pada agents |
|---|---|
| `opticargo-shared` | Kontrak request, state, recommendation, citation, dan respons API. |
| `opticargo-knowledge-graph` | Koneksi Neo4j serta context voyage, rute, pelabuhan, supplier, dan komoditas. |
| `opticargo-rag-pipeline` | Evidence regulasi, citation, dan abstention. |
| `opticargo-ml-models` | Scoring kandidat cargo match untuk optimasi. |
| `opticargo-infra` | Service discovery dan runtime container lokal. |

## Menjalankan lokal

Jalankan dependency melalui repository infra:

```powershell
cd "D:\PROYEK ML DAN AI\OptiCargo\opticargo-infra"
docker compose -f docker-compose.yml -f compose/overrides/local-build.yml --profile core --profile ai up -d neo4j qdrant rag-worker graph-worker ml-models agents
```

Periksa status:

```powershell
docker compose -f docker-compose.yml -f compose/overrides/local-build.yml --profile core --profile ai ps agents
```

Untuk pengembangan tanpa container, install dependency Python dari root workspace agar package Shared, RAG, dan Knowledge Graph tersedia pada interpreter yang sama.

## Konfigurasi penting

| Variabel | Kegunaan |
|---|---|
| `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` | Koneksi Knowledge Graph. |
| `QDRANT_URL`, `QDRANT_API_KEY` | Akses evidence RAG. |
| `ML_MODELS_INTERNAL_URL` | URL internal service scoring ML. |
| `INTERNAL_SERVICE_TOKEN` | Token antarlayanan, bila diaktifkan. |
| `LLM_API_KEY` atau `GROQ_API_KEY` | LLM untuk intent extraction, repair Cypher, dan narasi rekomendasi. |

Jangan menyimpan credential pada source, test fixture, log, atau README.

## Status dan pekerjaan integrasi

Alur route optimization telah tersedia: graph analysis → validasi Cypher → eksekusi Neo4j → optimasi → retrieval → recommendation.

Sebelum production, partner yang mengerjakan logic agents perlu menyelesaikan dan memverifikasi:

- migrasi node retrieval dari compatibility shim `hybrid_retrieve` ke typed retrieval `retrieve` dari RAG agar citation dan abstention dipertahankan end-to-end;
- deterministiknya ID kandidat yang dipetakan dari hasil Neo4j;
- perilaku kandidat backhaul, deduplikasi, dan constraint kapasitas;
- kontrak respons untuk fallback LLM/ML serta error dependency.

## Prinsip kontribusi

- Gunakan kontrak dari `opticargo-shared`; jangan membuat ulang model lintas repository.
- Semua Cypher yang dijalankan agents harus tervalidasi dan parameterized.
- Jawaban regulasi harus berdasarkan evidence RAG dan citation yang tersedia.
- Perubahan graph decision flow harus disertai test orchestrator dan test contract.
