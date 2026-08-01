# Test fixtures

Fixture dibagi berdasarkan boundary agar unit, contract, evaluation, dan E2E dapat memakai data reproducible tanpa production data.

| Folder | Isi |
|---|---|
| `requests/` | Gateway recommendation dan chat request examples. |
| `graph/` | Voyage context, candidate, route, dan analytics graph results. |
| `rag/` | Retrieved chunks, low-score evidence, dan empty result. |
| `ml/` | Trained/heuristic/invalid/hard-constraint scoring responses. |
| `sse/` | Complete, abstention, dan error event sequences. |
| `evaluation/` | Versioned cases untuk intent, citation, matching, dan abstention. |
| `expected/` | Golden typed responses yang berasal dari contract. |

Semua data file masih kosong. README pada masing-masing subfolder menetapkan aturan pengisiannya.
