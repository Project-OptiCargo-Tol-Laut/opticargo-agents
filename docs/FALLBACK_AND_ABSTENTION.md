# Fallback dan abstention

Fallback dan abstention adalah dua outcome berbeda.

## Fallback

Digunakan ketika hasil masih dapat diberikan secara aman melalui alternatif terdefinisi.

| Failure | Fallback |
|---|---|
| ML Models unavailable/invalid | Deterministic heuristic score; `fallback_used=true`, model mode heuristic. |
| LLM disabled/unavailable | Deterministic synthesis dari structured facts/evidence. |
| Optional enrichment gagal | Gunakan documented defaults bila tidak memengaruhi hard constraint; tambahkan warning. |

## Abstention

Digunakan ketika evidence/context minimum tidak tersedia.

| Kondisi | Outcome |
|---|---|
| Regulation tanpa valid citation/evidence | Abstain dan jelaskan evidence belum cukup. |
| Matching tanpa voyage context/candidate valid | Abstain/no-match; jangan membuat candidate. |
| Route membutuhkan graph tetapi graph unavailable | Abstain; jangan fabricated route. |
| Required dependency readiness gagal | HTTP 503 pada readiness; workflow behavior mengikuti typed policy. |

## Rules

- Fallback reason masuk trace/metrics dan response.
- Abstention reason wajib tersedia dan aman untuk caller.
- Default value tidak boleh digunakan untuk menutupi hard constraint atau missing identifier.
- Fallback quality diukur pada evaluation set dan tidak dipromosikan menjadi champion model.
