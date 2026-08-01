# Observability contract

## Metrics minimum

- request count/duration/result per internal endpoint;
- active request gauge;
- node duration/result;
- canonical intent count;
- fallback count by component/reason;
- tool/dependency error count;
- recommendation count by model mode/fallback;
- SSE event count;
- citation coverage;
- dependency readiness gauge;
- build/version info.

## Logs

Structured log minimum: UTC timestamp, level, service, release, Git SHA, correlation ID, endpoint/node, intent, duration, result, dependency, safe error code. Do not log token, API key, full prompt/evidence, raw provider body, payment data, atau user credential.

## Trace

Trace ID yang sama harus tersedia pada Gateway request, Agents log, node route, ML request, response header, dan SSE event.

## Alerts awal

- service unavailable >2 menit;
- readiness required dependency down;
- workflow error/timeout spike;
- node latency regression;
- ML fallback increase;
- citation coverage drop;
- no-match/abstention anomaly;
- active request saturation.
