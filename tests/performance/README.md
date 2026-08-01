# Performance tests

## Tujuan

Mengukur request, node, dependency, concurrency, dan SSE first-event latency pada workload terdefinisi.

## Kondisi eksekusi

Dijalankan pada environment terkontrol; tidak digabung dengan unit gate harian.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `test_recommendation_latency.py` | Mengukur `test_recommendation_latency.py` dengan warm-up, sample size, concurrency, percentile, dan resource profile yang dicatat. |
| `test_chat_time_to_first_event.py` | Mengukur `test_chat_time_to_first_event.py` dengan warm-up, sample size, concurrency, percentile, dan resource profile yang dicatat. |
| `test_node_latency.py` | Mengukur `test_node_latency.py` dengan warm-up, sample size, concurrency, percentile, dan resource profile yang dicatat. |
| `test_concurrent_requests.py` | Mengukur `test_concurrent_requests.py` dengan warm-up, sample size, concurrency, percentile, dan resource profile yang dicatat. |
| `test_ml_scoring_batch.py` | Mengukur `test_ml_scoring_batch.py` dengan warm-up, sample size, concurrency, percentile, dan resource profile yang dicatat. |
| `test_stream_backpressure.py` | Mengukur `test_stream_backpressure.py` dengan warm-up, sample size, concurrency, percentile, dan resource profile yang dicatat. |

## Evidence minimum

- p50/p95/p99.
- Error/fallback rate.
- CPU/memory.
- Dependency latency.
- Worker/concurrency configuration.

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
