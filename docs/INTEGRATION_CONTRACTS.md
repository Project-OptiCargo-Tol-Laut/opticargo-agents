# Integration contracts

## Gateway

- Producer request internal dan consumer response/SSE.
- Menyediakan authenticated user context, internal token, dan correlation ID.
- Menyimpan recommendation, audit, user decision, booking, dan payment.
- Tidak mengirim raw browser credential ke Agents.

## Knowledge Graph

Required operations:

- health;
- get voyage context;
- find backhaul candidates;
- enrich candidate;
- route context;
- graph overview;
- close.

Result harus memakai stable PostgreSQL-derived IDs dan typed fields. Query bersifat read-only.

## RAG

Required operations:

- health;
- retrieve(query, graph_context, top_k);
- close.

Result memuat citation metadata, score, excerpt, source/version/page/section. Agents tidak memanggil ingestion API.

## ML Models

Required operations:

- readiness;
- cargo-match scoring.

Request membawa internal token dan trace ID. Response memuat score, model mode/version, hard constraint flag, breakdown, explanation/warning. Invalid response dianggap dependency failure.

## Optional LLM

Required operations:

- health;
- optional intent classification;
- completion/stream;
- close.

Disabled mode wajib tersedia dan tidak melakukan network call. LLM failure tidak membuat keseluruhan service unavailable bila tidak diwajibkan readiness policy.
