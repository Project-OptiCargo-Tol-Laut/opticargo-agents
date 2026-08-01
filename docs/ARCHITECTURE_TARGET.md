# Arsitektur target

## Runtime boundary

```text
Frontend ──► Gateway API/BFF ──► Agents internal service
                                  ├── KG typed package ─► Neo4j
                                  ├── RAG typed package ► Qdrant
                                  └── ML Models HTTP ───► model service
```

Gateway melakukan user authentication, authorization, transaction mutation, audit, persistence recommendation, dan SSE proxy. Agents hanya menerima trusted internal request yang tetap harus divalidasi dan diautentikasi dengan service token.

## Composition

```text
FastAPI lifespan
  └── Runtime
      ├── KnowledgeGraphAdapter
      ├── RagAdapter
      ├── MLModelsClient
      ├── LLMClient / DisabledLLMClient
      ├── WorkflowRunner
      ├── OrchestrationService
      └── HealthService
```

## Dependency direction

```text
api ─► runtime/orchestrator/contracts/security/health
orchestrator ─► nodes/state/contracts/protocols
nodes ─► state/contracts/protocols/guardrails/metrics
integrations/clients ─► dependency packages or HTTP transport
contracts/config/errors/logging/metrics ─► dependency-minimal foundations
```

Concrete adapters tidak boleh diimpor oleh node. Node menerima ports sehingga unit test tidak membutuhkan live dependency.

## Data authority

- PostgreSQL/Gateway: source of truth transaksi dan persisted recommendation.
- Neo4j: reconstructable graph projection.
- Qdrant: reconstructable document index.
- ML Models: scoring response dengan model mode/version dan fallback metadata.
- Agents state: request-scoped temporary orchestration data, bukan durable store.

## Deployment

Agents berjalan sebagai internal-only container pada port container `8000` dengan command Infra:

```text
uvicorn opticargo_agents.api:app --host 0.0.0.0 --port 8000 --proxy-headers
```

Tidak ada public ingress atau direct browser route.
