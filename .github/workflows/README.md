# Workflows

| File | Gate yang direncanakan |
|---|---|
| `ci.yml.disabled` | Lint, type check, unit, architecture, contract, coverage, compile, build, package smoke. |
| `integration.yml.disabled` | LangGraph, ML HTTP, RAG/KG package, Gateway proxy, Prometheus, and shutdown integration. |
| `evaluation.yml.disabled` | Intent, hard constraint, citation, abstention, fallback, dan recommendation evaluation. |
| `release.yml.disabled` | Immutable wheel/image, SBOM, checksum, provenance, vulnerability scan, dan release manifest. |

Workflow tidak boleh diaktifkan dengan test placeholder atau permanent skip pada mandatory gate.
