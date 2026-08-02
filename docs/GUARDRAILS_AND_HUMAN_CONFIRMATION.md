# Guardrails dan human confirmation

## Input

- Bounded query length.
- Strict request fields dan canonical enum.
- User context hanya dari Gateway internal request.
- Text/prompt melewati secret redaction dan size limit.

## Evidence

- Regulation answer hanya memakai indexed evidence yang lolos threshold.
- Citation object berasal dari RAG metadata, bukan generated text.
- Full document content tidak dikirim ke log atau metric.

## Output

- Tidak boleh menyatakan booking/payment telah dibuat atau dibayar.
- Recommended action selalu mengarahkan pengguna meninjau dan mengonfirmasi melalui official UI/Gateway.
- LLM tidak mengubah identifier, score, hard constraint, model metadata, atau citation.
- Error/fallback/abstention disampaikan transparan.

## Transaction boundary

Agents tidak memiliki credential atau endpoint untuk transaction mutation. Enforcement dilakukan melalui architecture test, route inventory, dependency scan, security test, serta code review.
