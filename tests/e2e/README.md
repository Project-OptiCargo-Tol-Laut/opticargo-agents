# End-to-end tests

## Tujuan

Memverifikasi critical user-facing orchestration journey melalui Gateway-to-Agents boundary dan dependency aktual.

## Kondisi eksekusi

Memerlukan deterministic fixture/seed untuk Neo4j, Qdrant, dan ML response mode serta service readiness.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `test_matching_recommendation.py` | Menjalankan journey `test_matching_recommendation.py` dari request sampai structured response/SSE dan memeriksa ownership boundary. |
| `test_regulation_chat.py` | Menjalankan journey `test_regulation_chat.py` dari request sampai structured response/SSE dan memeriksa ownership boundary. |
| `test_route_chat.py` | Menjalankan journey `test_route_chat.py` dari request sampai structured response/SSE dan memeriksa ownership boundary. |
| `test_analytics_chat.py` | Menjalankan journey `test_analytics_chat.py` dari request sampai structured response/SSE dan memeriksa ownership boundary. |
| `test_unknown_clarification.py` | Menjalankan journey `test_unknown_clarification.py` dari request sampai structured response/SSE dan memeriksa ownership boundary. |
| `test_no_match_abstention.py` | Menjalankan journey `test_no_match_abstention.py` dari request sampai structured response/SSE dan memeriksa ownership boundary. |
| `test_regulation_no_evidence_abstention.py` | Menjalankan journey `test_regulation_no_evidence_abstention.py` dari request sampai structured response/SSE dan memeriksa ownership boundary. |
| `test_human_confirmation_boundary.py` | Menjalankan journey `test_human_confirmation_boundary.py` dari request sampai structured response/SSE dan memeriksa ownership boundary. |
| `test_sse_complete_sequence.py` | Menjalankan journey `test_sse_complete_sequence.py` dari request sampai structured response/SSE dan memeriksa ownership boundary. |

## Evidence minimum

- Correlation trace.
- Node route.
- Citation/evidence.
- Fallback/abstention flag.
- No transaction mutation proof.

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
