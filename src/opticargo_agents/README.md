# `opticargo_agents`

## Tujuan

Package utama internal orchestration service. Package ini menyatukan API, workflow, dependency adapter, guardrail, health, dan observability tanpa mengambil ownership transaksi dari Gateway.

## Posisi dalam alur runtime

Gateway memanggil endpoint internal pada `api.py`. `runtime.py` membangun dependency dan orchestration service. Workflow menghasilkan recommendation/chat answer, lalu Gateway menangani persistence, audit, serta konfirmasi transaksi.

## Tanggung jawab file

| File | Tanggung jawab | Perilaku yang diharapkan | Verifikasi utama |
|---|---|---|---|
| `__init__.py` | Public package surface. | Mengekspor version dan simbol stabil yang memang menjadi public package API; tidak menjalankan side effect saat import. | `tests/smoke/test_package_import.py` |
| `api.py` | FastAPI composition root dan route internal. | Menyediakan liveness, readiness, metrics, recommendation, dan chat SSE; memasang correlation middleware, auth dependency, lifespan, serta typed exception envelope. | `tests/unit/test_api.py` |
| `config.py` | Typed environment settings. | Membaca environment, memvalidasi URL/scheme/range, mengunci dependency version, dan menyimpan secret sebagai secret type. | `tests/unit/test_config.py` |
| `contracts.py` | Request/response dan trace contract. | Mendefinisikan strict models untuk Gateway recommendation, chat, citation, score breakdown, ranked cargo, node trace, health, dan error. | `tests/contract/test_gateway_contract.py` |
| `errors.py` | Typed domain/service error taxonomy. | Memetakan failure ke code, HTTP status, safe message, dan redacted details tanpa mengekspos raw dependency response. | `tests/unit/test_errors.py` |
| `guardrails.py` | Input/output safety guardrail. | Meredaksi pola secret, membatasi ukuran text, mencegah klaim mutation transaksi, dan menyiapkan evidence summary yang aman. | `tests/unit/test_guardrails.py` |
| `health.py` | Liveness/readiness aggregation. | Memeriksa dependency secara parallel sesuai readiness policy dan menghasilkan status `ready` atau `degraded` beserta timestamp. | `tests/unit/test_health.py` |
| `healthcheck.py` | Container healthcheck entrypoint. | Memanggil readiness endpoint dengan timeout pendek dan exit code yang dapat digunakan Docker/Kubernetes. | `tests/smoke/test_healthcheck_command.py` |
| `logging.py` | Structured logging dan correlation context. | Mengikat correlation ID ke context, menghasilkan JSON log allowlisted, dan tidak mencatat secret atau full evidence. | `tests/unit/test_logging.py` |
| `metrics.py` | Prometheus metric declarations. | Menyediakan request, node, intent, fallback, tool error, recommendation, stream, citation, dependency, concurrency, dan build metrics. | `tests/contract/test_metrics_contract.py` |
| `prompts.py` | Prompt policy dan prompt builder. | Menyimpan system policy yang grounded, human-confirmed, dan non-mutating; prompt tidak memuat secret atau data di luar context. | `tests/unit/test_prompts.py` |
| `protocols.py` | Dependency ports. | Mendefinisikan async interface untuk Knowledge Graph, RAG, ML Models, dan optional LLM agar node dapat diuji tanpa runtime aktual. | `tests/contract/test_dependency_protocols.py` |
| `runtime.py` | Dependency composition dan shutdown. | Membangun clients/adapters/runner/service/health satu kali, mengelola ownership lifecycle, dan menutup resource dengan urutan aman. | `tests/unit/test_runtime.py` |
| `security.py` | Internal request authentication. | Memverifikasi `X-Internal-Service-Token` menggunakan constant-time comparison dan menghasilkan typed unauthorized error. | `tests/unit/test_security.py` |
| `version.py` | Package version source. | Menyediakan version tunggal yang selaras dengan package metadata, image label, health, dan build info. | `tests/contract/test_version_contract.py` |
| `py.typed` | PEP 561 marker. | Menandai distribution sebagai typed package. | `tests/smoke/test_package_metadata.py` |

## Dependency dan contract

- `opticargo-shared==1.0.0` untuk enum/schema lintas repository.
- `opticargo-rag-pipeline==1.0.0` dan `opticargo-knowledge-graph==1.0.0` sebagai installable wheels.
- FastAPI/ASGI hanya sebagai internal transport dari Gateway.
- ML Models diakses melalui internal HTTP contract dan service token.

## Aturan desain

- Import package tidak boleh membuka network connection atau membaca secret secara eager.
- Semua request model memakai strict validation dan menolak extra field pada boundary.
- LLM tidak boleh mengubah hard constraint, score, identifier, citation, atau transactional state.
- Semua timeout, retry, concurrency, dan readiness policy bersifat explicit configuration.

## Observability

- Setiap request membawa correlation ID dan request duration.
- Node route menyimpan status, duration, fallback, dan safe detail.
- Dependency status tersedia melalui readiness dan `dependency_up` metric.
- Build metadata tersedia pada health dan Prometheus build info.

## Batas tanggung jawab

- Tidak menerima traffic browser langsung.
- Tidak menjadi source of truth atau persistence owner recommendation.
- Tidak membuat booking/payment dan tidak menyimpan payment credential.
- Tidak menulis Neo4j projection, Qdrant index, MLflow registry, atau MinIO artifact.

## Kriteria verifikasi

- Unit test memverifikasi jalur normal, input tidak valid, timeout, dan typed failure.
- Contract test memverifikasi request/response, event SSE, header internal, serta schema dependency lintas repository.
- Integration test hanya menggunakan dependency aktual pada layer adapter atau composition root.
- Implementasi tidak dianggap siap bila test hanya berisi placeholder, permanent skip, atau assertion yang tidak memeriksa perilaku.

> File implementasi pada struktur awal ini belum berisi kode. Dokumen ini menetapkan fungsi, contract, dan perilaku yang harus dipenuhi saat file tersebut diimplementasikan.
