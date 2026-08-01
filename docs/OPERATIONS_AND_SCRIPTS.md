# Operations and scripts

## Startup order

1. Infra stores and dependency services healthy.
2. Required wheels/image available.
3. Environment/secret validation.
4. Agents package/image preflight.
5. Agents start.
6. Liveness/readiness/metrics.
7. Gateway internal connectivity.
8. Recommendation/SSE smoke.

## Script contract

Setiap script harus:

- menerima path/environment secara explicit;
- memiliki `--help`;
- tidak mencetak secret;
- menggunakan non-zero exit pada failure;
- menghasilkan concise human output dan optional JSON output;
- memiliki timeout;
- tidak melakukan mutation bisnis.

## Shutdown

Stop accepting new requests, cancel/await in-flight work sesuai grace period, release semaphore, close HTTP/KG/RAG/LLM clients, lalu terminate.

## Recovery

Setelah dependency restart, readiness harus kembali sehat dan request baru berhasil tanpa restart manual Agents bila client mendukung reconnect. Bila tidak, runbook harus menyatakan restart procedure.
