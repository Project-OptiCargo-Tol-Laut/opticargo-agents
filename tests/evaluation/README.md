# Evaluation tests

## Tujuan

Mengukur kualitas routing, hard constraint, citation, abstention, recommendation schema, dan deterministic fallback.

## Kondisi eksekusi

Menggunakan versioned evaluation set dengan expected label/evidence. Hasil disimpan sebagai report, bukan hanya pass/fail tunggal.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `test_intent_classification_dataset.py` | Mengukur evaluation dimension `test_intent_classification_dataset.py` dengan threshold yang ditetapkan dan dataset versioned. |
| `test_hard_constraint_validity.py` | Mengukur evaluation dimension `test_hard_constraint_validity.py` dengan threshold yang ditetapkan dan dataset versioned. |
| `test_citation_correctness.py` | Mengukur evaluation dimension `test_citation_correctness.py` dengan threshold yang ditetapkan dan dataset versioned. |
| `test_abstention_quality.py` | Mengukur evaluation dimension `test_abstention_quality.py` dengan threshold yang ditetapkan dan dataset versioned. |
| `test_recommendation_schema_quality.py` | Mengukur evaluation dimension `test_recommendation_schema_quality.py` dengan threshold yang ditetapkan dan dataset versioned. |
| `test_fallback_consistency.py` | Mengukur evaluation dimension `test_fallback_consistency.py` dengan threshold yang ditetapkan dan dataset versioned. |
| `test_no_fabricated_source.py` | Mengukur evaluation dimension `test_no_fabricated_source.py` dengan threshold yang ditetapkan dan dataset versioned. |
| `test_no_mutation_claim.py` | Mengukur evaluation dimension `test_no_mutation_claim.py` dengan threshold yang ditetapkan dan dataset versioned. |

## Evidence minimum

- Dataset manifest/version.
- Metric dan threshold.
- Per-case failure list.
- Model/provider mode.
- Synthetic-data flag.

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
