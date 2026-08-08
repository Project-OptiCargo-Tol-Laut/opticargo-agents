"""Shared helpers for end-to-end journey tests.

Unlike tests/unit, which replace whole WorkflowNodes functions, e2e tests
here inject fakes at the *dependency boundary* only (RagAdapter's
retrieve_func, KnowledgeGraphAdapter's graph_query_func/session_factory,
MLModelsClient's transport). This means every real production node
(run_intent_node, run_graph_analysis_node, run_cargo_scoring_node,
run_retrieval_node, run_synthesis_node) and the real WorkflowRunner /
OrchestrationService run unmodified -- exactly the "request to structured
response/SSE" journey described in tests/e2e/README.md, without requiring a
live Neo4j/Qdrant/ML Models stack.
"""

from __future__ import annotations

from typing import Any, Callable
from uuid import uuid4

from opticargo_agents.clients.ml_models import MLModelsClient
from opticargo_agents.config import Settings, load_settings
from opticargo_agents.contracts import AgentRequest
from opticargo_agents.integrations import KnowledgeGraphAdapter, RagAdapter
from opticargo_agents.orchestrator.graph import WorkflowRunner
from opticargo_agents.orchestrator.service import OrchestrationService
from opticargo_agents.runtime import Runtime


class _NullSession:
    def __enter__(self) -> "_NullSession":
        return self

    def __exit__(self, *exc_info: object) -> bool:
        return False


class _FakeMLTransport:
    def __init__(self, response: dict[str, Any] | None = None, error: Exception | None = None) -> None:
        self._response = response
        self._error = error

    def post_json(
        self, url: str, payload: dict[str, Any], headers: dict[str, str], timeout: float
    ) -> dict[str, Any]:
        if self._error is not None:
            raise self._error
        return self._response or {}


def build_service(
    *,
    settings: Settings | None = None,
    graph_query_func: Callable[..., Any] | None = None,
    retrieve_func: Callable[..., Any] | None = None,
    ml_response: dict[str, Any] | None = None,
    ml_error: Exception | None = None,
) -> OrchestrationService:
    active_settings = settings or load_settings({})
    knowledge_graph = KnowledgeGraphAdapter(
        active_settings,
        graph_query_func=graph_query_func,
        session_factory=(lambda: _NullSession()) if graph_query_func is not None else None,
    )
    # Keep performance/e2e journeys deterministic and independent of a live
    # Qdrant or embedding model unless a test explicitly injects another
    # retrieval boundary.
    rag = RagAdapter(active_settings, retrieve_func=retrieve_func or regulation_retrieve)
    ml_models = MLModelsClient(active_settings, transport=_FakeMLTransport(ml_response, ml_error))
    runtime = Runtime(settings=active_settings, rag=rag, knowledge_graph=knowledge_graph, ml_models=ml_models)
    return OrchestrationService(runner=WorkflowRunner(runtime=runtime), settings=active_settings)


def make_request(**overrides: Any) -> AgentRequest:
    defaults: dict[str, Any] = {"query": "halo", "voyage_id": uuid4()}
    defaults.update(overrides)
    return AgentRequest(**defaults)


def voyage_graph_context(*, candidates: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """A realistic Knowledge Graph payload shape for one voyage leg."""
    candidate_list = candidates if candidates is not None else [_default_candidate()]
    return {
        "voyage_id": str(uuid4()),
        "active_leg": {
            "route_id": str(uuid4()),
            "route_type": "tol_laut",
            "distance_nm": 120,
            "estimated_days": 3,
            "origin_port": {"port_id": str(uuid4()), "name": "Sorong"},
            "destination_port": {"port_id": str(uuid4()), "name": "Makassar"},
        },
        "ship_capacity": {
            "total_weight_ton": 100,
            "used_weight_ton": 20,
            "remaining_weight_ton": 80,
            "remaining_volume_m3": 160,
        },
        "candidates": candidate_list,
    }


def _default_candidate() -> dict[str, Any]:
    return {
        "cargo_listing_id": str(uuid4()),
        "commodity_id": str(uuid4()),
        "commodity_name": "Semen",
        "available_weight_ton": 25,
        "available_volume_m3": 40,
        "capacity_compatible": True,
        "certification_compatible": True,
        "schedule_compatible": True,
        "origin_port": {"port_id": str(uuid4()), "name": "Makassar"},
        "destination_port": {"port_id": str(uuid4()), "name": "Sorong"},
        "supplier": {
            "supplier_id": str(uuid4()),
            "supplier_name": "Supplier Kandidat",
            "rating": 4.5,
            "verified": True,
            "avg_monthly_volume_ton": 120,
            "distance_to_port_nm": 10,
            "supplied_commodity_ids": [str(uuid4())],
        },
    }


def regulation_retrieve(query: str, *, graph_context: Any, top_k: int, min_score: float) -> dict[str, Any]:
    return {
        "query": query,
        "chunks": [{"text": "Pasal 12 mengatur muatan balik Tol Laut.", "score": 0.82}],
        "citations": [
            {
                "document_id": "PM-99-2023",
                "title": "Permenhub 99/2023 tentang Tol Laut",
                "page": 12,
                "excerpt": "Muatan balik wajib memenuhi syarat kelayakan dan sertifikasi komoditas.",
            }
        ],
        "confidence": 0.82,
        "abstained": False,
    }


def regulation_retrieve_no_citation(
    query: str, *, graph_context: Any, top_k: int, min_score: float
) -> dict[str, Any]:
    return {"query": query, "chunks": [], "citations": [], "confidence": None, "abstained": False}


def successful_ml_response(**overrides: Any) -> dict[str, Any]:
    payload = {
        "score": 0.82,
        "model_mode": "trained",
        "model_version": "1.0.0",
        "fallback_used": False,
        "hard_constraint_valid": True,
        "feature_explanations": [],
        "warnings": [],
    }
    payload.update(overrides)
    return payload
