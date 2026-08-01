# Node behavior

## Intent node

Menghasilkan canonical intent. Input request intent diprioritaskan. Heuristic harus deterministic dan language-aware. Optional LLM result hanya diterima bila termasuk enum yang valid.

## Graph analysis node

- Matching: voyage context dan canonical backhaul candidates.
- Route: route/path context berdasarkan query dan optional voyage.
- Analytics: graph overview/analytics query.
- Missing voyage atau graph failure pada required route menghasilkan abstention, bukan fabricated context.

## Optimization node

1. Membentuk payload feature dari voyage dan candidate.
2. Memanggil ML Models dengan trace ID.
3. Memvalidasi response dan model metadata.
4. Menghapus candidate `hard_constraint_valid=false`.
5. Mengurutkan score secara deterministic dengan stable tie-breaker.
6. Saat ML gagal, menjalankan documented heuristic fallback dan menandai fallback.

Heuristic hanya graceful degradation dan tidak boleh diklaim sebagai trained model.

## Retrieval node

Menjalankan hybrid RAG dengan query, graph context, top-k, dan minimum score. Citation memuat document ID, title, issuer, version, page/section, source reference, dan bounded excerpt. Regulation tanpa sufficient evidence harus abstain.

## Synthesis node

Mengubah structured state menjadi recommendation atau chat answer. LLM hanya boleh memperbaiki bahasa berdasarkan fakta yang diberikan. Identifier, score, hard constraint, citation, model metadata, dan human action tetap berasal dari structured state.

## Common node wrapper

Menyediakan timing, trace append, safe error detail, timeout/cancellation behavior, dan metrics. Wrapper tidak boleh mengubah typed failure menjadi silent success.
