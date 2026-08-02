# `nodes`

## Tujuan

Node workflow yang melakukan satu tanggung jawab terukur dan memutasi hanya workflow state. Node harus composable, typed, observable, timeout-aware, dan memiliki fallback/abstention yang eksplisit.

## Posisi dalam alur runtime

Orchestrator memilih node berdasarkan intent. Output node menjadi input node berikutnya; node tidak mengirim HTTP response atau persistence mutation secara langsung.

## Tanggung jawab file

| File | Tanggung jawab | Perilaku yang diharapkan | Verifikasi utama |
|---|---|---|---|
| `__init__.py` | Node package export. | Mengekspor callable node yang memang bagian workflow contract. | `tests/unit/nodes/test_exports.py` |
| `common.py` | Shared node execution helper. | Mengukur duration, menangani typed failure, menambahkan route trace, menerapkan timeout/retry policy yang sesuai, dan mempertahankan correlation context. | `tests/unit/nodes/test_common.py` |
| `intent.py` | Intent classification. | Memakai request intent bila valid, deterministic Indonesian heuristic, optional LLM refinement, lalu mempertahankan `unknown` bila confidence tidak cukup. | `tests/unit/nodes/test_intent.py` |
| `graph_analysis.py` | Graph context acquisition. | Untuk matching mengambil voyage/candidate; untuk route mengambil route context; untuk analytics mengambil overview; menetapkan abstention bila required context tidak tersedia. | `tests/unit/nodes/test_graph_analysis.py` |
| `optimization.py` | Cargo-match scoring dan hard filtering. | Membangun feature payload, memanggil ML, menormalisasi response, menolak hard constraint invalid, menggunakan heuristic fallback saat ML gagal, dan menghasilkan ranking deterministic. | `tests/unit/nodes/test_optimization.py` |
| `retrieval.py` | RAG evidence retrieval. | Mengirim query dan graph context, memfilter score, membentuk citation valid, serta abstain pada regulation flow ketika evidence tidak memadai. | `tests/unit/nodes/test_retrieval.py` |
| `synthesis.py` | Structured recommendation dan chat synthesis. | Menghasilkan Gateway-persistable recommendation atau chat answer, memakai optional LLM hanya untuk wording, mempertahankan facts/scores/citations, dan mencegah klaim mutation. | `tests/unit/nodes/test_synthesis.py` |

## Dependency dan contract

- Workflow state dari `orchestrator/state.py`.
- Ports pada `protocols.py`; node tidak bergantung pada concrete transport.
- Shared enum untuk canonical intent dan model mode.
- Guardrail, metrics, logging, dan trace contract.

## Aturan desain

- Setiap node harus idempotent terhadap state input yang sama selama dependency result sama.
- Node yang dilewati tidak boleh mengisi state palsu; field tetap `None`/empty sesuai contract.
- Hard constraint invalid tidak boleh masuk ranked output meskipun score tinggi.
- Fallback dan abstention adalah status berbeda dan harus terlihat pada response.
- LLM tidak boleh menjadi satu-satunya sumber intent, score, citation, atau recommended action.

## Observability

- Node duration histogram dengan node/result.
- Intent counter, fallback counter, tool error counter, citation coverage.
- Route trace menyimpan completed/skipped/failed/fallback serta safe detail.

## Batas tanggung jawab

- Tidak membuat HTTP response langsung.
- Tidak mengelola client lifecycle.
- Tidak mempersist recommendation atau user feedback.
- Tidak menjalankan transaction mutation atau provider payment call.

## Kriteria verifikasi

- Unit test memverifikasi jalur normal, input tidak valid, timeout, dan typed failure.
- Contract test memverifikasi request/response, event SSE, header internal, serta schema dependency lintas repository.
- Integration test hanya menggunakan dependency aktual pada layer adapter atau composition root.
- Implementasi tidak dianggap siap bila test hanya berisi placeholder, permanent skip, atau assertion yang tidak memeriksa perilaku.

> File implementasi pada struktur awal ini belum berisi kode. Dokumen ini menetapkan fungsi, contract, dan perilaku yang harus dipenuhi saat file tersebut diimplementasikan.
