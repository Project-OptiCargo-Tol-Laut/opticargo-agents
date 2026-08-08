"""Shared helpers for performance tests.

Reuses the e2e fake-adapter-boundary harness (tests/e2e/_support.py) so
performance measurements exercise the REAL production pipeline (intent,
graph analysis, optimization, retrieval, synthesis, orchestrator) with
deterministic, near-instant fake dependencies -- measuring our own code's
overhead, not network latency to Neo4j/Qdrant/ML Models.
"""

from __future__ import annotations

from tests.e2e._support import (
    build_service,
    make_request,
    regulation_retrieve,
    successful_ml_response,
    voyage_graph_context,
)

__all__ = [
    "build_service",
    "make_request",
    "regulation_retrieve",
    "successful_ml_response",
    "voyage_graph_context",
]