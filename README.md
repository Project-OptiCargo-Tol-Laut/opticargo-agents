# opticargo-agents

Service inti kecerdasan buatan OptiCargo AI. Mengorkestrasikan 5 AI Agent
menggunakan LangGraph untuk menghasilkan rekomendasi backhaul, jawaban chat
kontekstual, dan dokumen booking.

> Catatan desain: kelima agent digabung dalam satu service untuk kecepatan
> development MVP, tetapi ditulis sebagai modul terisolasi (state, tools,
> dan I/O jelas per-agent) agar mudah dipecah jadi microservice terpisah
> pasca-MVP (lihat roadmap di opticargo-docs).

## 5 Agent

| Agent | Fungsi Singkat |
|---|---|
| Data Ingestion Agent | Mengumpulkan, membersihkan, validasi, index data ke PostgreSQL/Qdrant/Neo4j |
| Retrieval Agent | Vector search (Qdrant) + graph query (Neo4j) + hybrid re-ranking |
| Graph Analysis Agent | Analisis pola di Knowledge Graph, scoring peluang backhaul |
| Optimization Agent | Knapsack/constraint solver untuk kombinasi muatan optimal |
| Recommendation Agent | Sintesis akhir: narasi rekomendasi, draft dokumen, notifikasi |

## Tech Stack
- Python, LangGraph (orchestration & state management)
- LLM: Gemini (via API)
- Terhubung ke Qdrant (vector), Neo4j (graph) via `opticargo-rag-pipeline` dan `opticargo-knowledge-graph`

## Struktur Direktori
    /agents/ingestion
    /agents/retrieval
    /agents/graph_analysis
    /agents/optimization
    /agents/recommendation
    /orchestrator        → LangGraph graph definition, state schema
    /tools               → tool implementations dipakai lintas agent

## Dependensi Repo Lain
- `opticargo-shared` — tipe state LangGraph & schema request/response antar agent.
- `opticargo-rag-pipeline` — retriever, embedding, Qdrant client.
- `opticargo-knowledge-graph` — Cypher query library untuk Neo4j.
- Dipanggil oleh `opticargo-gateway-api`.

## Menjalankan Lokal
    pip install -r requirements.txt
    python -m orchestrator.serve   # expose sebagai HTTP/gRPC service