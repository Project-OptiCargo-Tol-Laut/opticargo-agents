# `integrations`

## Tujuan

Adapter terhadap installable packages Knowledge Graph dan RAG. Adapter mengubah API package menjadi ports yang dibutuhkan workflow tanpa mengimpor sibling source tree.

## Posisi dalam alur runtime

Graph analysis node menggunakan Knowledge Graph adapter. Retrieval node menggunakan RAG adapter. Health service memakai kedua adapter untuk readiness.

## Tanggung jawab file

| File | Tanggung jawab | Perilaku yang diharapkan | Verifikasi utama |
|---|---|---|---|
| `__init__.py` | Package export. | Mengekspor adapter/factory yang stabil dan tidak menginisialisasi client secara global. | `tests/unit/integrations/test_exports.py` |
| `knowledge_graph.py` | Knowledge Graph query adapter. | Mengambil voyage context, backhaul candidate, candidate enrichment, route context, graph overview, health, dan close melalui typed package API. | `tests/unit/integrations/test_knowledge_graph.py` |
| `rag.py` | RAG query adapter. | Menjalankan hybrid retrieval dengan graph context, top-k, minimum score, citation metadata, health, dan close melalui typed package API. | `tests/unit/integrations/test_rag.py` |

## Dependency dan contract

- `opticargo-knowledge-graph==1.0.0` typed query package.
- `opticargo-rag-pipeline==1.0.0` hybrid retrieval package.
- Neo4j/Qdrant connection settings diteruskan sesuai API package, bukan diduplikasi sembarang.

## Aturan desain

- Stable domain IDs berasal dari source projection dan tidak diganti UUID acak.
- Adapter tidak memakai private symbol dependency package.
- Graph query bersifat read-only; RAG adapter tidak melakukan ingestion.
- Missing dependency package harus menghasilkan startup/doctor error yang jelas.

## Observability

- Graph query latency, result count, timeout, dan failure.
- RAG retrieval latency, citation count, score distribution, dan failure.
- Package version dependency tercatat pada doctor/build metadata.

## Batas tanggung jawab

- Tidak menulis Neo4j projection.
- Tidak mengindeks atau menghapus document chunk.
- Tidak melakukan scoring ML atau synthesis.
- Tidak mengakses PostgreSQL transaksi secara langsung.

## Kriteria verifikasi

- Unit test memverifikasi jalur normal, input tidak valid, timeout, dan typed failure.
- Contract test memverifikasi request/response, event SSE, header internal, serta schema dependency lintas repository.
- Integration test hanya menggunakan dependency aktual pada layer adapter atau composition root.
- Implementasi tidak dianggap siap bila test hanya berisi placeholder, permanent skip, atau assertion yang tidak memeriksa perilaku.

> File implementasi pada struktur awal ini belum berisi kode. Dokumen ini menetapkan fungsi, contract, dan perilaku yang harus dipenuhi saat file tersebut diimplementasikan.
