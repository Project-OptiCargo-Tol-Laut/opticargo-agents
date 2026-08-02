# Implementation flow

## Phase 0 — Contracts

- Shared enum/schema/version.
- Gateway request/response/SSE/error contract.
- RAG/KG package ports.
- ML Models scoring contract.
- Canonical intent, route, state, fallback, and abstention.

## Phase 1 — Package foundation

- `pyproject.toml`, version, config, errors, contracts, protocols.
- logging, metrics, security, guardrails.
- architecture/contract/unit foundations.

## Phase 2 — Dependency adapters

- ML Models client.
- LLM disabled/provider client.
- Knowledge Graph adapter.
- RAG adapter.
- Adapter unit and live integration tests.

## Phase 3 — Workflow nodes

- Intent.
- Graph analysis.
- Optimization and hard filter.
- Retrieval and citation.
- Synthesis and human-confirmation guardrail.

## Phase 4 — Orchestration

- Workflow state.
- Deterministic runner.
- Compiled LangGraph with parity tests.
- Timeout, semaphore, cancellation, route trace.

## Phase 5 — Internal API

- FastAPI lifespan/runtime.
- Auth/correlation middleware.
- Health/readiness/metrics.
- Recommendation and SSE endpoints.

## Phase 6 — Packaging and Infra

- Wheel/image, non-root, healthcheck.
- Compose/Kubernetes contract.
- Prometheus/Grafana/alerts.
- Setup, runbook, troubleshooting.

## Phase 7 — Hardening

- E2E, fault injection, performance, security, evaluation.
- Release manifest, checksum, SBOM, rollback, known limitations.

Dependency order tidak boleh dibalik: contract package dan RAG/KG query APIs harus stabil sebelum final workflow/Agents integration.
