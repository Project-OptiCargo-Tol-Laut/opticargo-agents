from pathlib import Path
import sys
from uuid import uuid4

SHARED_SRC = Path(__file__).resolve().parents[3] / "opticargo-shared" / "src"
if SHARED_SRC.exists():
    sys.path.insert(0, str(SHARED_SRC))

from opticargo_agents.config import load_settings
from opticargo_agents.contracts import AgentRequest, GraphContextResult
from opticargo_agents.orchestrator.graph import build_cargo_scoring_payload
from opticargo_shared.enums import QueryIntent  # noqa: E402


def test_agents_intents_match_shared_query_intents() -> None:
    assert {item.value for item in QueryIntent} == {
        "regulation",
        "matching",
        "route",
        "analytics",
        "unknown",
    }


def test_graph_to_ml_payload_contains_required_top_level_fields() -> None:
    payload = build_cargo_scoring_payload(
        AgentRequest(query="matching", voyage_id=uuid4()),
        GraphContextResult(
            context={
                "voyage_id": str(uuid4()),
                "active_leg": {"route_id": str(uuid4()), "distance_nm": "10"},
                "ship_capacity": {"remaining_weight_ton": "20", "remaining_volume_m3": "30"},
                "candidates": [
                    {
                        "cargo_listing_id": str(uuid4()),
                        "available_weight_ton": "5",
                        "supplier": {"supplier_id": str(uuid4()), "rating": "0.8"},
                    }
                ],
            }
        ),
        load_settings({}),
    )

    assert {"trace_id", "voyage", "candidate"} <= set(payload)
    assert {"voyage_id", "remaining_weight_ton"} <= set(payload["voyage"])
    assert {"cargo_listing_id", "supplier_id", "cargo_weight_ton"} <= set(payload["candidate"])
