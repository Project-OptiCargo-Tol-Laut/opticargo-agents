# Chat SSE contract

## Event types

| Event | Tujuan |
|---|---|
| `meta` | Trace ID, accepted request metadata, dan stream version; dikirim segera. |
| `status` | Node/phase progress yang aman untuk caller. |
| `citation` | Citation object yang telah divalidasi. |
| `token` | Bounded text chunk untuk answer. |
| `done` | Final structured metadata: intent, confidence, fallback, abstention, route. |
| `error` | Safe terminal error envelope. |

## Rules

- Content type `text/event-stream`.
- `Cache-Control: no-cache`, proxy buffering disabled, dan internal timeout policy terdokumentasi.
- Exactly one terminal event: `done` atau `error`.
- `meta` dikirim sebelum long-running workflow agar trace tersedia.
- Citation dikirim sebelum atau bersama text yang merujuknya.
- Token chunk tidak memotong encoding invalid dan memiliki maximum size.
- Cancellation client menghentikan pekerjaan dan melepaskan semaphore/resource.
- Raw stack trace, secret, full prompt, full document, dan provider body tidak masuk stream.
