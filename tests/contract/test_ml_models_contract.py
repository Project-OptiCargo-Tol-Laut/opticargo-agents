"""Contract layer: pastikan payload yang benar-benar dikirim ke ML Models
(via build_cargo_scoring_payload) valid terhadap skema resmi
opticargo-ml-models (CargoMatchRequest), bukan cuma "terlihat masuk akal".
"""

from uuid import uuid4

from opticargo_ml_models.contracts import CargoMatchRequest

from opticargo_agents.config import load_settings
from opticargo_agents.contracts import AgentRequest, GraphContextResult
from opticargo_agents.orchestrator.graph import build_cargo_scoring_payload


def _graph_context() -> GraphContextResult:
    return GraphContextResult(
        context={
            "voyage_id": str(uuid4()),
            "active_leg": {
                "route_id": str(uuid4()),
                "route_type": "tol_laut",
                "distance_nm": "120",
                "estimated_days": 3,
                "origin_port": {"port_id": str(uuid4()), "name": "Sorong"},
                "destination_port": {"port_id": str(uuid4()), "name": "Makassar"},
            },
            "ship_capacity": {
                "total_weight_ton": "100",
                "used_weight_ton": "20",
                "remaining_weight_ton": "80",
                "remaining_volume_m3": "160",
            },
            "candidates": [
                {
                    "cargo_listing_id": str(uuid4()),
                    "commodity_id": str(uuid4()),
                    "available_weight_ton": "25",
                    "available_volume_m3": "40",
                    "certification_compatible": True,
                    "schedule_compatible": True,
                    "origin_port": {"port_id": str(uuid4()), "name": "Makassar"},
                    "destination_port": {"port_id": str(uuid4()), "name": "Sorong"},
                    "supplier": {
                        "supplier_id": str(uuid4()),
                        "rating": "4.5",
                        "verified": True,
                        "avg_monthly_volume_ton": "120",
                        "distance_to_port_nm": "10",
                        "supplied_commodity_ids": [str(uuid4())],
                    },
                }
            ],
        }
    )


def test_build_cargo_scoring_payload_matches_ml_models_contract() -> None:
    request = AgentRequest(query="matching", voyage_id=uuid4())
    payload = build_cargo_scoring_payload(request, _graph_context(), load_settings({}))

    assert payload is not None

    validated = CargoMatchRequest.model_validate(payload)

    assert validated.voyage.remaining_weight_ton == 80
    assert validated.candidate.supplier_rating == 4.5
    assert validated.candidate.certification_match is True


def test_build_cargo_scoring_payload_returns_none_when_graph_context_missing() -> None:
    request = AgentRequest(query="matching", voyage_id=uuid4())
    payload = build_cargo_scoring_payload(request, None, load_settings({}))

    assert payload is None