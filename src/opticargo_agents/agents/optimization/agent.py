import os
import requests
from decimal import Decimal
from opticargo_agents.orchestrator.state import OrchestratorState
from opticargo_shared.agent_state.optimization import OptimizationOutput

def optimization_node(state: OrchestratorState) -> dict:
    """
    Node untuk agen Optimasi.
    Memanggil API opticargo-ml-models (yang dibuat oleh tim ML)
    untuk melakukan scoring dan knapsack constraint solving pada kandidat.
    """
    candidates = state.graph_analysis_result.candidates if state.graph_analysis_result else []
    
    # Siapkan payload
    payload = {
        "voyage_id": state.voyage_id,
        "remaining_capacity_ton": None, # Akan di-resolve oleh ML service berdasarkan voyage_id jika ada
        "candidates": [
            {
                "supplier_id": str(c.supplier_id),
                "commodity_id": str(c.commodity_id),
                "volume_ton": float(c.volume_ton)
            } for c in candidates
        ]
    }
    
    ml_url = os.getenv("OPTICARGO_ML_MODELS_URL", "http://localhost:8001")
    
    try:
        # Panggil service ML milik teman Anda
        response = requests.post(f"{ml_url}/api/v1/optimize", json=payload, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Parse hasil dari ML model
        # Asumsikan response mengembalikan selected_candidates dan estimasi revenue
        selected = candidates # Di skenario asli, filter berdasarkan ID dari response
        estimated_rev = Decimal(data.get("estimated_revenue", 0))
        
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
