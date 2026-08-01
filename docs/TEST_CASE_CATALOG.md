# Test case catalog

## Recommendation

- Valid matching request menghasilkan ranked valid candidates.
- Invalid/unknown request field ditolak.
- top-N range diterapkan.
- Hard constraint invalid selalu terhapus.
- ML trained mode metadata konsisten.
- ML failure menghasilkan heuristic fallback transparan.
- No valid candidate menghasilkan no-match/abstention, bukan fabricated candidate.

## Regulation

- Relevant evidence menghasilkan citations dan grounded answer.
- Low score/empty evidence menghasilkan abstention.
- Citation memuat source/version/page/section.
- LLM disabled tetap menghasilkan deterministic answer.
- Retrieved prompt injection tidak mengubah system policy atau transaction boundary.

## Route/analytics/unknown

- Graph context dipakai pada route/analytics.
- Graph unavailable menghasilkan abstention pada required flow.
- Unknown menghasilkan clarification, bukan forced intent.

## API/SSE

- Missing/wrong internal token ditolak.
- Correlation ID propagated.
- Validation error safe.
- SSE order dan exactly-one terminal event.
- Client disconnect membatalkan task dan melepaskan semaphore.

## Operations

- Liveness tidak bergantung dependency.
- Readiness mengikuti required policy.
- Metrics dapat discrape.
- Shutdown menutup clients.
- Image non-root dan healthcheck valid.
