# `orchestrator`

## Tujuan

Workflow state, conditional graph, deterministic runner, request-level timeout/concurrency, recommendation service, dan SSE event orchestration.

## Posisi dalam alur runtime

API memanggil OrchestrationService. Service membuat initial state, menjalankan WorkflowRunner, mengubah final state menjadi typed response, dan mengirim SSE event sesuai contract.

## Tanggung jawab file

| File | Tanggung jawab | Perilaku yang diharapkan | Verifikasi utama |
|---|---|---|---|
| `__init__.py` | Orchestrator package export. | Mengekspor state, runner, dan service yang stabil tanpa membangun runtime saat import. | `tests/unit/orchestrator/test_exports.py` |
| `state.py` | Mutable workflow state contract. | Menampung request context, intent, graph context, candidates, evidence, citations, score, fallback, abstention, error, trace, dan final answer secara typed. | `tests/unit/orchestrator/test_state.py` |
| `graph.py` | Conditional workflow definition dan runner. | Menyusun LangGraph route, memastikan semantic parity dengan deterministic manual runner, menerapkan skipped-node behavior, dan menghasilkan final state. | `tests/unit/orchestrator/test_graph.py` |
| `service.py` | Use-case service dan SSE delivery. | Membatasi concurrency, menerapkan global timeout, membuat recommendation/chat response, mengirim `meta/status/citation/token/done/error`, serta mengubah failure ke safe terminal event. | `tests/unit/orchestrator/test_service.py` |

## Dependency dan contract

- Node callable dari `nodes/`.
- Typed request/response dan NodeTrace dari `contracts.py`.
- Settings timeout/concurrency/top-n.
- LangGraph sebagai production graph runtime dengan deterministic fallback runner untuk parity/recovery.

## Aturan desain

- Route harus deterministic untuk intent dan precondition yang sama.
- Global timeout tidak boleh meninggalkan background task yang terus memakai dependency.
- Semaphore harus dilepas pada success, typed failure, timeout, dan cancellation.
- SSE `meta` dikirim sebelum pekerjaan lama; terminal event tepat satu.
- Manual runner dan compiled graph harus diuji dengan golden route cases.

## Observability

- Active request gauge, endpoint duration, route/node trace, timeout/fallback count.
- SSE event count per type dan time-to-first-event.
- Trace ID sama pada request, dependency call, response, dan stream event.

## Batas tanggung jawab

- Tidak mengimplementasikan business scoring detail di graph/service.
- Tidak menyimpan state lintas request secara global.
- Tidak melakukan booking/payment mutation atau persistence recommendation.
- Tidak mengubah raw LLM output menjadi fakta tanpa node validation.

## Kriteria verifikasi

- Unit test memverifikasi jalur normal, input tidak valid, timeout, dan typed failure.
- Contract test memverifikasi request/response, event SSE, header internal, serta schema dependency lintas repository.
- Integration test hanya menggunakan dependency aktual pada layer adapter atau composition root.
- Implementasi tidak dianggap siap bila test hanya berisi placeholder, permanent skip, atau assertion yang tidak memeriksa perilaku.

> File implementasi pada struktur awal ini belum berisi kode. Dokumen ini menetapkan fungsi, contract, dan perilaku yang harus dipenuhi saat file tersebut diimplementasikan.
