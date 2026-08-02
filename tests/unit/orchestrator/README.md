# Unit tests — orchestrator

## Tujuan

State, conditional route, manual/compiled parity, service timeout, semaphore, dan SSE.

## Kondisi eksekusi

Berjalan tanpa live Infra dan menggunakan deterministic fake/clock/transport.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `test_exports.py` | Memverifikasi perilaku `test_exports.py` sesuai README source terkait. |
| `test_state.py` | Memverifikasi perilaku `test_state.py` sesuai README source terkait. |
| `test_graph.py` | Memverifikasi perilaku `test_graph.py` sesuai README source terkait. |
| `test_service.py` | Memverifikasi perilaku `test_service.py` sesuai README source terkait. |

## Evidence minimum

- Input fixture.
- Expected return/state/exception.
- Metric/trace side effect bila relevan.

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
