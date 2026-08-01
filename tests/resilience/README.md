# Resilience tests

## Tujuan

Memastikan dependency failure, timeout, cancellation, restart, dan concurrency pressure menghasilkan fallback/abstention yang aman.

## Kondisi eksekusi

Menggunakan fault injection terkontrol dan tidak dijalankan terhadap production.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `test_ml_unavailable_fallback.py` | Menginjeksikan kondisi `test_ml_unavailable_fallback.py` dan memverifikasi typed response, bounded duration, trace, metric, serta resource cleanup. |
| `test_ml_retry_then_success.py` | Menginjeksikan kondisi `test_ml_retry_then_success.py` dan memverifikasi typed response, bounded duration, trace, metric, serta resource cleanup. |
| `test_ml_invalid_response_fallback.py` | Menginjeksikan kondisi `test_ml_invalid_response_fallback.py` dan memverifikasi typed response, bounded duration, trace, metric, serta resource cleanup. |
| `test_rag_unavailable_abstention.py` | Menginjeksikan kondisi `test_rag_unavailable_abstention.py` dan memverifikasi typed response, bounded duration, trace, metric, serta resource cleanup. |
| `test_graph_unavailable_abstention.py` | Menginjeksikan kondisi `test_graph_unavailable_abstention.py` dan memverifikasi typed response, bounded duration, trace, metric, serta resource cleanup. |
| `test_llm_unavailable_deterministic.py` | Menginjeksikan kondisi `test_llm_unavailable_deterministic.py` dan memverifikasi typed response, bounded duration, trace, metric, serta resource cleanup. |
| `test_global_workflow_timeout.py` | Menginjeksikan kondisi `test_global_workflow_timeout.py` dan memverifikasi typed response, bounded duration, trace, metric, serta resource cleanup. |
| `test_node_timeout.py` | Menginjeksikan kondisi `test_node_timeout.py` dan memverifikasi typed response, bounded duration, trace, metric, serta resource cleanup. |
| `test_bounded_concurrency.py` | Menginjeksikan kondisi `test_bounded_concurrency.py` dan memverifikasi typed response, bounded duration, trace, metric, serta resource cleanup. |
| `test_client_cancellation.py` | Menginjeksikan kondisi `test_client_cancellation.py` dan memverifikasi typed response, bounded duration, trace, metric, serta resource cleanup. |
| `test_dependency_restart_recovery.py` | Menginjeksikan kondisi `test_dependency_restart_recovery.py` dan memverifikasi typed response, bounded duration, trace, metric, serta resource cleanup. |
| `test_shutdown_during_request.py` | Menginjeksikan kondisi `test_shutdown_during_request.py` dan memverifikasi typed response, bounded duration, trace, metric, serta resource cleanup. |
| `test_partial_route_failure.py` | Menginjeksikan kondisi `test_partial_route_failure.py` dan memverifikasi typed response, bounded duration, trace, metric, serta resource cleanup. |

## Evidence minimum

- Fault injection timeline.
- Expected fallback/abstention.
- No leaked task/connection.
- Recovery evidence.

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
