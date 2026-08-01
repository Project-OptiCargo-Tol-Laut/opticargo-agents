# Scripts

Seluruh script pada folder ini masih kosong. Dokumen [`docs/OPERATIONS_AND_SCRIPTS.md`](../docs/OPERATIONS_AND_SCRIPTS.md) menetapkan input, output, exit code, redaction, dependency, dan expected behavior setiap script.

| Script | Kegunaan |
|---|---|
| `bootstrap.py` | Membuat virtual environment, memeriksa Python, dan menginstal wheel/dependency secara reproducible. |
| `validate.py` | Menjalankan lint, type check, unit/contract test, coverage, compile, build, dan artifact inspection. |
| `smoke_structure.py` | Memeriksa struktur repository serta policy file kosong pada initial state. |
| `smoke_env.py` | Memvalidasi key/range/URL environment tanpa mencetak secret. |
| `smoke_packages.py` | Memastikan Shared, RAG, KG, dan Agents distribution/version kompatibel. |
| `smoke_infra.py` | Memeriksa DNS/TCP/HTTP readiness dependency sesuai host atau container mode. |
| `smoke_internal_api.py` | Memeriksa liveness, readiness, auth negative case, dan recommendation contract. |
| `smoke_sse.py` | Memeriksa content type, event order, trace ID, terminal event, dan timeout stream. |
| `smoke_metrics.py` | Memastikan `/metrics` dapat discrape dan metric minimum tersedia. |
| `build_dependency_wheels.py` | Membangun/menyalin wheel Shared, RAG, dan KG dari source/tag resmi serta menghasilkan checksum manifest. |
| `run-local.*` | Menjalankan service pada loopback dengan environment lokal yang eksplisit. |
| `build-image.*` | Membangun image immutable, non-root, dan berlabel release/Git SHA. |
| `demo-preflight.*` | Menjalankan preflight berurutan sebelum demo atau staging freeze. |

Script tidak boleh mengubah database, graph, index, atau secret secara diam-diam. Semua operasi consequential memerlukan command dan environment yang jelas.
