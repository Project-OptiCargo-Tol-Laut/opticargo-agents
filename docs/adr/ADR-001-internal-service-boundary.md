# ADR-001 — Internal service boundary

- Status: Proposed

## Decision

Agents berjalan sebagai internal-only service. Browser tidak memanggil Agents langsung. Gateway tetap owner authentication, authorization, transaction, audit, persistence, dan SSE proxy.

## Consequence

Endpoint bisnis Agents berada di `/internal/v1/*`, memakai service token, dan tidak memiliki public ingress.
