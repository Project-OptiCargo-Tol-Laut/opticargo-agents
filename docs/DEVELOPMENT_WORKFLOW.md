# Development workflow

## Change size

Satu perubahan sebaiknya menyelesaikan satu behavior yang dapat diuji, misalnya Settings validation, ML client retry, regulation abstention, atau SSE terminal event.

## Branch dan commit

Gunakan Conventional Commit yang jelas. Commit dapat dibuat per file/per responsibility agar review mudah ditelusuri, misalnya:

```text
feat(config): tambahkan validasi environment agents
feat(contracts): definisikan kontrak rekomendasi internal
feat(nodes): implementasikan klasifikasi intent deterministik
test(nodes): tambahkan pengujian klasifikasi intent
```

## Pull request evidence

- requirement dan acceptance;
- contract/version impact;
- route/state/node impact;
- fallback/abstention behavior;
- tests and coverage;
- observability/security impact;
- setup/deploy/rollback bila relevan.

## Review order

1. Contract dan boundary.
2. Failure/fallback/abstention.
3. Tests.
4. Source implementation.
5. Observability/security.
6. Documentation/operations.
