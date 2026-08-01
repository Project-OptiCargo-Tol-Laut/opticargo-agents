# Unit tests — cli

## Tujuan

Doctor output, exit code, redaction, dan dependency summary.

## Kondisi eksekusi

Berjalan tanpa live Infra dan menggunakan deterministic fake/clock/transport.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `test_exports.py` | Memverifikasi perilaku `test_exports.py` sesuai README source terkait. |
| `test_doctor.py` | Memverifikasi perilaku `test_doctor.py` sesuai README source terkait. |

## Evidence minimum

- Input fixture.
- Expected return/state/exception.
- Metric/trace side effect bila relevan.

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
