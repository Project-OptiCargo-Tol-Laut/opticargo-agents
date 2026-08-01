# Workflow state

Workflow state bersifat request-scoped dan tidak dipersist oleh Agents.

## Kelompok field

### Request identity

- trace/correlation ID;
- query;
- requested/canonical intent;
- voyage ID;
- user ID dan role;
- top-N.

### Graph context

- voyage/ship/route/capacity context;
- route/analytics context;
- raw candidate list;
- optional candidate enrichment.

### Retrieval context

- retrieved chunks;
- validated citations;
- retrieval scores/coverage.

### Optimization context

- feature payload;
- scored candidates;
- model mode/version;
- hard constraint result;
- fallback reason.

### Control and output

- node route trace;
- errors/warnings;
- fallback flag;
- abstained flag and reason;
- answer/recommendation;
- confidence.

## Invariants

- Trace ID tersedia sebelum node pertama.
- `abstained=true` selalu memiliki reason.
- Candidate hard constraint invalid tidak masuk final ranking.
- Citation final berasal dari validated retrieved metadata.
- Model mode/version dan fallback flag konsisten antara candidate, breakdown, item, dan response.
- Error internal tidak disalin mentah ke answer/SSE.
