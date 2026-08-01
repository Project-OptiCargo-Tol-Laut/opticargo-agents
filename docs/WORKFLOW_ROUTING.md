# Workflow routing

## Canonical intents

| Intent | Required context | Route | Success result |
|---|---|---|---|
| `regulation` | Query text | intent → retrieval → synthesis | Grounded answer with citations. |
| `matching` | Voyage ID | intent → graph → optimization → retrieval → synthesis | Ranked backhaul recommendation. |
| `route` | Query, optional voyage ID | intent → graph → retrieval → synthesis | Route context answer. |
| `analytics` | Query | intent → graph → synthesis | Graph projection summary/analytics. |
| `unknown` | Query | intent → synthesis | Clarification and supported capability list. |

## Classification priority

1. Valid intent supplied by Gateway.
2. Deterministic Indonesian keyword/rule classifier.
3. Optional LLM classifier only when still unknown.
4. Preserve unknown when confidence is insufficient.

## Skipped node rules

Node yang tidak diperlukan tidak dijalankan dan tidak mengisi fabricated state. Trace boleh menandai `skipped` bila contract route memerlukannya. Skipped field tetap `None`, empty list, atau default yang dijelaskan pada state contract.

## Compiled/manual parity

Compiled LangGraph dan deterministic runner harus menghasilkan route, state outcome, fallback/abstention, dan response yang semantically sama untuk golden input. Manual runner bukan shortcut yang menghilangkan guardrail atau dependency behavior.
