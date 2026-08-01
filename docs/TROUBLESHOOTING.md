# Troubleshooting

## Agents cannot start

Check configuration validation, required wheel installation/version, internal token, dependency URL scheme, and import error. Do not bypass validation with hardcoded default.

## Readiness returns 503

Inspect per-dependency status for ML Models, Neo4j, Qdrant, and optional LLM policy. Validate internal DNS, credentials, network, database/collection availability, and timeout.

## Recommendation returns no result

Verify voyage ID exists in graph projection, candidate query result, capacity/time/radius/compatibility hard constraints, ML response, and fallback trace.

## Regulation abstains unexpectedly

Check Qdrant collection/index version, document active/superseded status, retrieval score threshold, citation metadata, and RAG package health.

## SSE stops or buffers

Check Gateway/Nginx buffering settings, content type, timeout, client disconnect, exactly-one terminal event, and correlation trace. Do not expose direct public Agents port as workaround.

## Fallback rate increases

Inspect dependency readiness, tool error metric, ML latency/response validation, model mode/version, and recent deployment. Fallback is a signal, not a permanent normal state.

## Secret appears in logs

Treat as security incident: stop exposure, rotate secret, preserve safe evidence, fix redaction/allowlist, and add regression test.
