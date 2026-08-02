# Unit tests — clients

## Tujuan

HTTP/provider client behavior dengan mock transport, timeout, retry, validation, dan close.

## Kondisi eksekusi

Berjalan tanpa live Infra dan menggunakan deterministic fake/clock/transport.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `test_exports.py` | Memverifikasi perilaku `test_exports.py` sesuai README source terkait. |
| `test_llm.py` | Memverifikasi perilaku `test_llm.py` sesuai README source terkait. |
| `test_ml_models.py` | Memverifikasi perilaku `test_ml_models.py` sesuai README source terkait. |

## Evidence minimum

- Input fixture.
- Expected return/state/exception.
- Metric/trace side effect bila relevan.

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
