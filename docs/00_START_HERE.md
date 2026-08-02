# Mulai dari sini

## Tujuan struktur

Struktur ini mempertahankan daftar module dan perilaku penting dari implementasi referensi, tetapi tidak membawa code implementation. README per folder dan catalog berfungsi sebagai specification awal.

## Urutan membaca

1. `REVIEW_BASIS.md`
2. `EXISTING_IMPLEMENTATION_REVIEW.md`
3. `ARCHITECTURE_TARGET.md`
4. `INTERNAL_API_CONTRACT.md`
5. `WORKFLOW_ROUTING.md`
6. `WORKFLOW_STATE.md`
7. `NODE_BEHAVIOR.md`
8. `INTEGRATION_CONTRACTS.md`
9. `FALLBACK_AND_ABSTENTION.md`
10. `TESTING_STRATEGY.md`
11. `IMPLEMENTATION_FLOW.md`
12. `DEFINITION_OF_DONE.md`

## Gate sebelum mengisi source

- Contract `opticargo-shared`, RAG, KG, ML Models, dan Gateway tersedia serta versioned.
- Endpoint internal, header auth, SSE event, and error envelope disepakati.
- Canonical intent, workflow route, state field, fallback, dan abstention policy disepakati.
- Infra service names/ports serta secret injection disepakati.
- Evaluation dataset dan acceptance threshold minimal didefinisikan.
- File test target telah dipilih untuk perubahan pertama.

## Prinsip kerja

Satu perubahan mengimplementasikan satu behavior yang dapat diuji. README dan contract menjadi acuan; test membuktikan behavior; source memenuhi test. Hindari satu perubahan besar yang sekaligus mengisi API, seluruh workflow, semua clients, dan seluruh E2E.
