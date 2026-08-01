# Security tests

## Tujuan

Memverifikasi internal authentication, redaction, route exposure, prompt boundary, URL validation, dan larangan credential/mutation.

## Kondisi eksekusi

Berjalan tanpa production secret dan menggunakan synthetic sensitive strings.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `test_internal_token_required.py` | Memverifikasi security property `test_internal_token_required.py` termasuk positive dan negative case. |
| `test_internal_token_constant_time.py` | Memverifikasi security property `test_internal_token_constant_time.py` termasuk positive dan negative case. |
| `test_secret_redaction.py` | Memverifikasi security property `test_secret_redaction.py` termasuk positive dan negative case. |
| `test_error_response_redaction.py` | Memverifikasi security property `test_error_response_redaction.py` termasuk positive dan negative case. |
| `test_prompt_injection_boundary.py` | Memverifikasi security property `test_prompt_injection_boundary.py` termasuk positive dan negative case. |
| `test_no_public_business_routes.py` | Memverifikasi security property `test_no_public_business_routes.py` termasuk positive dan negative case. |
| `test_no_transaction_credentials.py` | Memverifikasi security property `test_no_transaction_credentials.py` termasuk positive dan negative case. |
| `test_openapi_policy.py` | Memverifikasi security property `test_openapi_policy.py` termasuk positive dan negative case. |
| `test_log_allowlist.py` | Memverifikasi security property `test_log_allowlist.py` termasuk positive dan negative case. |
| `test_dependency_url_validation.py` | Memverifikasi security property `test_dependency_url_validation.py` termasuk positive dan negative case. |

## Evidence minimum

- Unauthorized response.
- Redacted logs/errors.
- Route inventory.
- Static secret scan.
- Prompt/output safety evidence.

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
