# Internal API contract

## Common headers

| Header | Arah | Aturan |
|---|---|---|
| `X-Internal-Service-Token` | Gateway → Agents | Wajib pada `/internal/v1/*`; dibandingkan constant-time; tidak dicatat pada log. |
| `X-Correlation-ID` | Dua arah | UUID valid diteruskan; invalid/missing diganti dengan UUID baru; sama pada dependency call dan response. |
| `Accept: text/event-stream` | Gateway → chat stream | Digunakan untuk SSE endpoint. |

## Health dan metrics

- `GET /health/live`: hanya membuktikan process/event loop dapat merespons.
- `GET /health/ready`: mengagregasi required dependency sesuai environment policy; degraded required dependency menghasilkan HTTP 503.
- `GET /metrics`: Prometheus exposition, hanya tersedia pada internal network.

## Recommendation

```text
POST /internal/v1/recommendations
```

Input minimum:

- `voyage_id`: stable UUID.
- `top_n`: bounded positive integer.
- `intent`: fixed `matching` untuk endpoint ini.

Output minimum:

- recommendations list;
- aggregate confidence;
- fallback flag;
- trace ID;
- node route;
- per-item ranked cargo, score breakdown, risk, alternative, citation, model mode, dan recommended human action.

## Chat stream

```text
POST /internal/v1/chat/stream
```

Input minimum:

- query;
- optional canonical intent;
- optional voyage ID;
- authenticated user ID dan role dari Gateway context.

SSE event order:

```text
meta -> status* -> citation* -> token* -> done
```

Failure terminal event adalah `error`. Stream harus memiliki exactly one terminal event, tidak mengekspos secret/raw dependency response, dan selalu membawa trace ID.

## Compatibility

Perubahan field, enum, status, endpoint, header, atau SSE event memerlukan versioning/compatibility test serta koordinasi Gateway consumer.
