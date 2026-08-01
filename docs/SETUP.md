# Setup

## Prerequisites

- Python version approved by `pyproject.toml` after implementation.
- Official Shared, RAG, and Knowledge Graph wheels.
- Access to Infra environment or loopback mappings for ML Models, Neo4j, and Qdrant.
- Internal service token and dependency credentials supplied through local secret handling.

## Intended workflow

1. Create clean virtual environment.
2. Install dependency wheels.
3. Install Agents in editable mode for development.
4. Copy `config/agents.env.example` to local `.env` and fill approved values.
5. Run structure/config/package smoke.
6. Run unit/contract/architecture tests.
7. Start dependency stack.
8. Run live smoke and integration.
9. Start Agents on loopback or through Infra.

Exact commands are activated only after `pyproject.toml` and scripts are implemented; until then the repository is a documented structure, not a runnable package.
