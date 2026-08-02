# Unit tests — nodes

## Tujuan

Setiap workflow node, state mutation, route trace, fallback, dan abstention.

## Kondisi eksekusi

Berjalan tanpa live Infra dan menggunakan deterministic fake/clock/transport.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `test_exports.py` | Memverifikasi perilaku `test_exports.py` sesuai README source terkait. |
| `test_common.py` | Memverifikasi perilaku `test_common.py` sesuai README source terkait. |
| `test_intent.py` | Memverifikasi perilaku `test_intent.py` sesuai README source terkait. |
| `test_graph_analysis.py` | Memverifikasi perilaku `test_graph_analysis.py` sesuai README source terkait. |
| `test_optimization.py` | Memverifikasi perilaku `test_optimization.py` sesuai README source terkait. |
| `test_retrieval.py` | Memverifikasi perilaku `test_retrieval.py` sesuai README source terkait. |
| `test_synthesis.py` | Memverifikasi perilaku `test_synthesis.py` sesuai README source terkait. |

## Evidence minimum

- Input fixture.
- Expected return/state/exception.
- Metric/trace side effect bila relevan.

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
