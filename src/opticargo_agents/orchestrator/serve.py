from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from opticargo_agents.orchestrator.graph import build_graph
from opticargo_agents.orchestrator.state import OrchestratorState

app = FastAPI(
    title="OptiCargo AI Agents Orchestrator",
    description="LangGraph Orchestrator for 4 Core AI Agents",
    version="1.0.0"
)

# Init graph
agent_graph = build_graph()

class RecommendRequest(BaseModel):
    request_id: str
    query: str
    request_type: str = "general"
    voyage_id: Optional[str] = None

@app.post("/recommend")
async def recommend(req: RecommendRequest):
    """
    Endpoint utama yang menjalankan keseluruhan graf (Retrieval -> Recommendation).
    """
    # Inisiasi state awal
    initial_state = OrchestratorState(
        request_id=req.request_id,
        query=req.query,
        request_type=req.request_type,
        voyage_id=req.voyage_id,
        trace=[]
    )
    
    try:
        # Jalankan StateGraph LangGraph (menjalankan aliran dari entry point sampai END)
        final_state = agent_graph.invoke(initial_state)
        
        return {
            "status": "success",
            "request_id": final_state.get("request_id"),
            "trace": final_state.get("trace"),
            "recommendation": final_state.get("final_recommendation", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Endpoint untuk mengecek apakah orchestrator hidup."""
    return {"status": "healthy", "service": "opticargo-agents"}
