# Unit tests

## Tujuan

Memverifikasi module root menggunakan fake ports dan deterministic input.

## Kondisi eksekusi

Tidak menggunakan network, filesystem global, service runtime, atau environment secret nyata.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `test_api.py` | Memverifikasi module `api` pada normal, invalid, boundary, dan failure paths. |
| `test_config.py` | Memverifikasi module `config` pada normal, invalid, boundary, dan failure paths. |
| `test_contracts.py` | Memverifikasi module `contracts` pada normal, invalid, boundary, dan failure paths. |
| `test_errors.py` | Memverifikasi module `errors` pada normal, invalid, boundary, dan failure paths. |
| `test_guardrails.py` | Memverifikasi module `guardrails` pada normal, invalid, boundary, dan failure paths. |
| `test_health.py` | Memverifikasi module `health` pada normal, invalid, boundary, dan failure paths. |
| `test_healthcheck.py` | Memverifikasi module `healthcheck` pada normal, invalid, boundary, dan failure paths. |
| `test_logging.py` | Memverifikasi module `logging` pada normal, invalid, boundary, dan failure paths. |
| `test_metrics.py` | Memverifikasi module `metrics` pada normal, invalid, boundary, dan failure paths. |
| `test_prompts.py` | Memverifikasi module `prompts` pada normal, invalid, boundary, dan failure paths. |
| `test_protocols.py` | Memverifikasi module `protocols` pada normal, invalid, boundary, dan failure paths. |
| `test_runtime.py` | Memverifikasi module `runtime` pada normal, invalid, boundary, dan failure paths. |
| `test_security.py` | Memverifikasi module `security` pada normal, invalid, boundary, dan failure paths. |
| `test_version.py` | Memverifikasi module `version` pada normal, invalid, boundary, dan failure paths. |

## Evidence minimum

- Branch coverage module.
- Typed exception/assertion.
- No network proof melalui fake transport.

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
