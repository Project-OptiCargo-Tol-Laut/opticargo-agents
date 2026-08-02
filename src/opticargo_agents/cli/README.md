# `cli`

## Tujuan

Command operasional untuk memeriksa package version, configuration, dependency wheel, DNS/connectivity, health, dan readiness sebelum service masuk staging.

## Posisi dalam alur runtime

CLI dijalankan dari developer environment, CI, container preflight, atau runbook. CLI tidak menjadi daemon dan tidak menjalankan use case bisnis.

## Tanggung jawab file

| File | Tanggung jawab | Perilaku yang diharapkan | Verifikasi utama |
|---|---|---|---|
| `__init__.py` | CLI package marker. | Tidak melakukan side effect. | `tests/unit/cli/test_exports.py` |
| `doctor.py` | Environment/dependency doctor. | Memeriksa config, package versions, internal URLs, Neo4j/Qdrant/ML health, optional LLM policy, dan menghasilkan exit code serta safe summary. | `tests/unit/cli/test_doctor.py` |

## Dependency dan contract

- Settings model dan package metadata.
- Health/readiness ports dengan timeout pendek.
- Infra internal DNS contract.

## Aturan desain

- Tidak mencetak secret atau full connection string yang berisi credential.
- Output machine-readable harus stabil untuk CI.
- Failure satu dependency harus terlihat per component, bukan hanya generic failure.

## Observability

- Doctor duration dan per-dependency result pada log lokal/CI bila diperlukan.

## Batas tanggung jawab

- Tidak memulai FastAPI server.
- Tidak menjalankan recommendation/chat workflow.
- Tidak memperbaiki environment secara otomatis.

## Kriteria verifikasi

- Unit test memverifikasi jalur normal, input tidak valid, timeout, dan typed failure.
- Contract test memverifikasi request/response, event SSE, header internal, serta schema dependency lintas repository.
- Integration test hanya menggunakan dependency aktual pada layer adapter atau composition root.
- Implementasi tidak dianggap siap bila test hanya berisi placeholder, permanent skip, atau assertion yang tidak memeriksa perilaku.

> File implementasi pada struktur awal ini belum berisi kode. Dokumen ini menetapkan fungsi, contract, dan perilaku yang harus dipenuhi saat file tersebut diimplementasikan.
