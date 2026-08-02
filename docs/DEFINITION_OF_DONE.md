# Definition of Done

## Per behavior

- Source, test, and README/catalog consistent.
- Typed contract dan failure behavior selesai.
- Unit/contract/architecture test lulus.
- Security/redaction/ownership boundary diperiksa.
- Metrics/log/trace tersedia bila relevan.
- Tidak ada secret, hardcoded production response, fabricated citation, atau silent fallback.

## Per integration

- Official dependency wheel/version/checksum digunakan.
- Live integration dan cleanup lulus.
- Timeout/retry/cancellation/recovery diuji.
- Correlation ID dapat ditelusuri.
- Runbook dan troubleshooting diperbarui.

## Per release

- All mandatory tests and evaluation threshold pass.
- Immutable wheel/image, non-root, healthcheck, SBOM, checksum, provenance, and vulnerability scan available.
- Staging Gateway-to-Agents recommendation and SSE pass.
- Prometheus/Grafana/alerts pass.
- Rollback and known limitations documented.
- Demo preflight succeeds from clean/reproducible state.
