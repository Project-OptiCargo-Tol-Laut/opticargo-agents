import os
import requests
from decimal import Decimal
from uuid import uuid4
from opticargo_agents.orchestrator.state import OrchestratorState
from opticargo_shared.agent_state.optimization import OptimizationOutput


def _cargo_match_payload(state: OrchestratorState, candidate) -> dict:
    cargo_weight_ton = max(float(candidate.volume_ton), 0.01)
    return {
        "voyage": {
            "voyage_id": state.voyage_id or str(uuid4()),
            "route_id": str(uuid4()),
            "route_distance_km": 1000.0,
            "remaining_weight_ton": max(cargo_weight_ton * 3, 1.0),
            "remaining_volume_m3": max(cargo_weight_ton * 6, 1.0),
            "operating_cost_per_km_idr": 125000.0,
        },
        "candidate": {
            "cargo_listing_id": str(candidate.cargo_listing_id or uuid4()),
            "supplier_id": str(candidate.supplier_id),
            "cargo_weight_ton": cargo_weight_ton,
            "cargo_volume_m3": max(cargo_weight_ton * 2, 0.01),
            "asking_price_per_ton_idr": 900000.0,
            "market_rate_per_ton_idr": 1000000.0,
            "origin_distance_km": 25.0,
            "destination_distance_km": 25.0,
            "schedule_gap_hours": 12.0,
            "supplier_rating": 4.2,
            "supplier_success_rate": 0.9,
            "supplier_cancellation_rate": 0.05,
            "commodity_compatibility": candidate.certification_compatible is not False,
            "certification_match": candidate.certification_compatible is not False,
            "temperature_match": True,
            "weather_risk": 0.2,
            "port_congestion": 0.3,
            "historical_acceptance_rate": 0.85,
        },
        "trace_id": str(state.request_id),
    }

def optimization_node(state: OrchestratorState) -> dict:
    """
    Node untuk agen Optimasi.
    Memanggil API opticargo-ml-models (yang dibuat oleh tim ML)
    untuk melakukan scoring dan knapsack constraint solving pada kandidat.
    """
    candidates = state.graph_analysis_result.candidates if state.graph_analysis_result else []
    
    ml_url = os.getenv(
        "ML_MODELS_INTERNAL_URL",
        os.getenv("OPTICARGO_ML_MODELS_URL", "http://ml-models:8000"),
    )
    token = os.getenv("INTERNAL_SERVICE_TOKEN")
    headers = {"X-Internal-Service-Token": token} if token else {}
    
    try:
        scored = []
        for candidate in candidates:
            response = requests.post(
                f"{ml_url}/v1/score/cargo-match",
                json=_cargo_match_payload(state, candidate),
                headers=headers,
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()
            scored.append((Decimal(str(data.get("score", "0"))), candidate))

        scored.sort(key=lambda item: item[0], reverse=True)
        selected = [candidate for score, candidate in scored if score >= Decimal("0.4")][:3]
        estimated_rev = Decimal(
            sum(float(candidate.volume_ton) * 1_000_000 * float(score) for score, candidate in scored[:3])
        )
        
    except (requests.exceptions.RequestException, Exception) as e:
        # FALLBACK: Jika API ML mati/belum siap, gunakan pendekatan greedy heuristic sederhana
        selected = sorted(candidates, key=lambda x: x.volume_ton, reverse=True)[:3]
        estimated_rev = Decimal(sum([float(c.volume_ton) * 1000 for c in selected]))

    output = OptimizationOutput(
        request_id=state.request_id,
        selected_candidates=selected,
        estimated_total_revenue=estimated_rev
    )
    
    return {"optimization_result": output, "trace": state.trace + ["optimization"]}
