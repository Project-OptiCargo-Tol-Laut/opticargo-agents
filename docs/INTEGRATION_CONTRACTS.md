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

Agents membangun payload scoring dari `GraphContext` final `opticargo-shared` terlebih dahulu melalui `build_shared_cargo_scoring_payload`. Payload shared ini berisi `correlation_id`, `voyage`, `candidate`, `route_schedule`, dan `supplier_risk`. Untuk menjaga kompatibilitas dengan runtime `opticargo-ml-models` saat ini, payload shared tersebut kemudian ditransformasikan menjadi bentuk legacy strict ML Models sebelum dikirim ke endpoint `/v1/score/cargo-match`.

Field KG yang dipakai untuk scoring:

- voyage: `voyage_id`, `route_id`, `origin_port_id`, `destination_port_id`, kapasitas berat/volume;
- route schedule: `distance_nm`, `estimated_days`, `route_type`, `schedule_compatible`;
- candidate: `cargo_listing_id`, `commodity_id`, origin/destination port, `available_weight_ton`, `available_volume_m3`;
- supplier risk: `supplier_id`, rating skala 1-5, `verified`, `avg_monthly_volume_ton`, dan jarak ke port.

## Optional LLM

Required operations:

- health;
- optional intent classification;
- completion/stream;
- close.

Disabled mode wajib tersedia dan tidak melakukan network call. LLM failure tidak membuat keseluruhan service unavailable bila tidak diwajibkan readiness policy.
