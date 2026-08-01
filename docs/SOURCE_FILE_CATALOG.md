# Source file catalog

Seluruh file source masih kosong. Catalog ini menjelaskan peran target.

| File | Target responsibility |
|---|---|
| `src/opticargo_agents/__init__.py` | Stable package exports and version. |
| `src/opticargo_agents/api.py` | FastAPI internal routes, middleware, lifespan, errors, health, metrics, recommendation, and SSE. |
| `src/opticargo_agents/config.py` | Typed environment settings and validation. |
| `src/opticargo_agents/contracts.py` | Strict Gateway/Agents request, response, citation, score, trace, health, and error models. |
| `src/opticargo_agents/errors.py` | Typed service/dependency/workflow errors. |
| `src/opticargo_agents/guardrails.py` | Redaction, size limits, grounding/output/transaction guardrails. |
| `src/opticargo_agents/health.py` | Dependency readiness aggregation. |
| `src/opticargo_agents/healthcheck.py` | Container readiness command. |
| `src/opticargo_agents/logging.py` | Correlation-aware structured logging. |
| `src/opticargo_agents/metrics.py` | Prometheus metric declarations. |
| `src/opticargo_agents/prompts.py` | Grounded system and task prompt builders. |
| `src/opticargo_agents/protocols.py` | Ports for KG, RAG, ML, and LLM. |
| `src/opticargo_agents/runtime.py` | Composition and lifecycle. |
| `src/opticargo_agents/security.py` | Internal token authentication. |
| `src/opticargo_agents/version.py` | Package version source. |
| `src/opticargo_agents/py.typed` | PEP 561 typed marker. |
| `src/opticargo_agents/cli/__init__.py` | Package marker/export with no import side effect. |
| `src/opticargo_agents/cli/doctor.py` | Configuration/dependency preflight. |
| `src/opticargo_agents/clients/__init__.py` | Package marker/export with no import side effect. |
| `src/opticargo_agents/clients/llm.py` | Disabled and OpenAI-compatible optional LLM clients. |
| `src/opticargo_agents/clients/ml_models.py` | Internal ML scoring/readiness HTTP client. |
| `src/opticargo_agents/integrations/__init__.py` | Package marker/export with no import side effect. |
| `src/opticargo_agents/integrations/knowledge_graph.py` | Typed KG package adapter. |
| `src/opticargo_agents/integrations/rag.py` | Typed RAG package adapter. |
| `src/opticargo_agents/nodes/__init__.py` | Package marker/export with no import side effect. |
| `src/opticargo_agents/nodes/common.py` | Node timing/trace/error wrapper. |
| `src/opticargo_agents/nodes/intent.py` | Canonical intent classification. |
| `src/opticargo_agents/nodes/graph_analysis.py` | Matching/route/analytics graph context. |
| `src/opticargo_agents/nodes/optimization.py` | ML/heuristic scoring and hard filtering. |
| `src/opticargo_agents/nodes/retrieval.py` | Evidence retrieval and citation validation. |
| `src/opticargo_agents/nodes/synthesis.py` | Structured recommendation/chat answer. |
| `src/opticargo_agents/orchestrator/__init__.py` | Package marker/export with no import side effect. |
| `src/opticargo_agents/orchestrator/state.py` | Request-scoped workflow state. |
| `src/opticargo_agents/orchestrator/graph.py` | Conditional graph and deterministic parity runner. |
| `src/opticargo_agents/orchestrator/service.py` | Use cases, timeout/concurrency, and SSE delivery. |
