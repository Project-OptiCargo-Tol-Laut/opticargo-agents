# Repository structure

```text
opticargo-agents/
├── src/opticargo_agents/
│   ├── api/config/contracts/security/health/observability foundations
│   ├── clients/          internal HTTP/provider clients
│   ├── integrations/     installed Knowledge Graph and RAG package adapters
│   ├── nodes/            intent, graph, optimization, retrieval, synthesis
│   ├── orchestrator/     state, conditional graph, service, SSE use cases
│   └── cli/              operational doctor
├── tests/
│   ├── architecture/ contract/ unit/ smoke/
│   ├── integration/ e2e/ resilience/
│   ├── evaluation/ performance/ security/
│   └── fixtures/
├── docs/                 contracts, design, operations, testing, ADR
├── config/               Infra reference and Agents env keys
├── scripts/              empty operational command placeholders
├── vendor/               optional offline dependency wheels
└── .github/              templates and disabled workflows
```

## Design intent

- Root foundations tetap dependency-minimal.
- Concrete dependency access berada pada `clients/` dan `integrations/`.
- Business orchestration berada pada `nodes/` dan `orchestrator/`.
- API menjadi transport/composition boundary, bukan tempat scoring atau retrieval logic.
- Tests disusun berdasarkan jenis evidence, bukan menumpuk seluruh case pada satu folder.
