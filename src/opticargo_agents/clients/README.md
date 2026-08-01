# `clients`

## Tujuan

HTTP/provider clients untuk dependency yang memang berbentuk service. Client harus menyembunyikan transport detail dari node serta mengembalikan typed, validated result.

## Posisi dalam alur runtime

ML Models dipanggil dari optimization node. LLM bersifat optional untuk intent refinement atau synthesis; deterministic behavior tetap tersedia ketika LLM disabled/unavailable.

## Tanggung jawab file

| File | Tanggung jawab | Perilaku yang diharapkan | Verifikasi utama |
|---|---|---|---|
| `__init__.py` | Package export. | Mengekspor factory/client type yang stabil tanpa membuat connection saat import. | `tests/unit/clients/test_exports.py` |
| `llm.py` | Provider-neutral OpenAI-compatible LLM client dan disabled implementation. | Mendukung health, optional intent classification, completion, stream, timeout, safe parsing, dan close; disabled mode tidak melakukan network call. | `tests/unit/clients/test_llm.py` |
| `ml_models.py` | Internal ML Models HTTP client. | Memanggil readiness dan cargo-match scoring dengan internal token/correlation ID, timeout, bounded retry, response validation, dan typed dependency error. | `tests/unit/clients/test_ml_models.py` |

## Dependency dan contract

- Internal service token dan correlation ID dari runtime context.
- ML scoring contract dari `opticargo-shared` atau versioned internal API.
- OpenAI-compatible schema hanya berlaku pada adapter LLM, bukan domain contract Agents.

## Aturan desain

- Retry hanya untuk failure yang aman dan idempotent.
- Jangan log request header secret, full prompt, full evidence, atau raw provider body.
- Response dependency harus divalidasi sebelum diteruskan ke node.
- LLM output merupakan untrusted text dan selalu melewati guardrail/contract synthesis.

## Observability

- Dependency latency, success/failure, retry count, dan fallback reason.
- Readiness gauge per dependency.
- Tool error metric menggunakan label ber-cardinality rendah.

## Batas tanggung jawab

- Tidak memiliki business routing.
- Tidak membuat heuristic recommendation.
- Tidak mengubah transaction atau projection.
- Tidak menyimpan response provider secara permanen.

## Kriteria verifikasi

- Unit test memverifikasi jalur normal, input tidak valid, timeout, dan typed failure.
- Contract test memverifikasi request/response, event SSE, header internal, serta schema dependency lintas repository.
- Integration test hanya menggunakan dependency aktual pada layer adapter atau composition root.
- Implementasi tidak dianggap siap bila test hanya berisi placeholder, permanent skip, atau assertion yang tidak memeriksa perilaku.

> File implementasi pada struktur awal ini belum berisi kode. Dokumen ini menetapkan fungsi, contract, dan perilaku yang harus dipenuhi saat file tersebut diimplementasikan.
