# Security boundary

## Trust model

Agents berada pada private network tetapi setiap internal request tetap diautentikasi dan divalidasi. Internal network bukan pengganti auth.

## Controls

- Constant-time service-token comparison.
- Secret types dan no production-like default.
- Strict request validation dan bounded text.
- Correlation ID validation.
- Dependency URL scheme/range validation.
- Prompt/evidence/output redaction.
- Safe error and SSE envelope.
- No public business routes.
- No booking/payment mutation dependency.
- Non-root immutable container dan read-only filesystem where feasible.
- Dependency pinning, checksum, SBOM, and vulnerability scan.

## Data minimization

Agents menerima hanya user context dan domain identifiers yang diperlukan. Full document, payment credential, raw card/provider payload, password/hash, dan unrelated PII tidak boleh masuk request/state/log.

## Prompt injection boundary

Retrieved document dan user query adalah untrusted content. System policy, structured facts, hard constraint, citations, and transaction boundary cannot be overridden by retrieved text or LLM output.
