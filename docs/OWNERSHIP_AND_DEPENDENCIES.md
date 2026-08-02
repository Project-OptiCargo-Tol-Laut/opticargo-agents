# Ownership and dependencies

| Component | Owns | Does not own |
|---|---|---|
| Gateway | User auth, RBAC, transactions, audit, recommendation persistence, SSE proxy | Graph/RAG/ML orchestration detail. |
| Agents | Intent, workflow, graph/RAG tool use, scoring orchestration, synthesis, fallback/abstention, trace | Transaction mutation, durable source of truth. |
| Knowledge Graph | Neo4j projection/query package, sync/reconciliation | PostgreSQL transaction ownership. |
| RAG Pipeline | Ingestion worker, Qdrant index, retrieval/citation package | Document upload transaction, answer synthesis. |
| ML Models | Scoring/model mode/version/fallback service, registry lifecycle | Booking/payment, graph/RAG data ownership. |
| Shared | Versioned schemas/enums/events/errors | Runtime connection or business orchestration. |
| Infra | Network, stores, secrets, deployment, monitoring, backup/rollback | Business logic/schema duplication. |

## Runtime dependency

Gateway → Agents → RAG/KG packages and ML HTTP. Agents has no direct dependency on frontend, payment provider, PostgreSQL transaction repository, MinIO report store, or MLflow.
