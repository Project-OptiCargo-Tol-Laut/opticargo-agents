from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Response
from pydantic import AliasChoices, BaseModel, Field

from opticargo_agents.orchestrator.graph import build_graph
from opticargo_agents.orchestrator.state import OrchestratorState
from opticargo_shared.agent_state import RecommendationOutput
from opticargo_shared.api import RecommendResponse
from opticargo_shared.enums import ConfidenceLevel, QueryIntent

app = FastAPI(
    title="OptiCargo AI Agents Orchestrator",
    description="LangGraph Orchestrator for 4 Core AI Agents",
    version="1.0.0"
)

# Init graph
agent_graph = build_graph()


class RecommendRequest(BaseModel):
    correlation_id: UUID | None = Field(
        default=None,
        validation_alias=AliasChoices("correlation_id", "request_id"),
    )
    user_id: UUID | None = None
    query: str
    request_type: str = "general"
    voyage_id: Optional[UUID] = None


def _intent_from_state(intent_type: str | None) -> QueryIntent:
    mapping = {
        "REGULATION_QUERY": QueryIntent.regulation,
        "ROUTE_OPTIMIZATION": QueryIntent.route,
        "GENERAL_CHAT": QueryIntent.unknown,
        "OUT_OF_SCOPE": QueryIntent.unknown,
    }
    return mapping.get(intent_type or "", QueryIntent.unknown)


def _confidence_level(score: Decimal) -> ConfidenceLevel:
    if score >= Decimal("0.75"):
        return ConfidenceLevel.high
    if score >= Decimal("0.4"):
        return ConfidenceLevel.medium
    return ConfidenceLevel.low


def _response_from_final_state(
    correlation_id: UUID,
    voyage_id: UUID | None,
    final_state: dict,
) -> RecommendResponse:
    def state_get(name: str, default=None):
        if isinstance(final_state, dict):
            return final_state.get(name, default)
        return getattr(final_state, name, default)

    final_recommendation = state_get("final_recommendation")
    recommendation = getattr(final_recommendation, "final_recommendation", None)
    content = getattr(recommendation, "content", None)
    summary = getattr(content, "summary", None)

    if not summary:
        return RecommendResponse(
            correlation_id=correlation_id,
            status="failed",
            errors=["Recommendation agent did not produce a summary"],
        )

    confidence = Decimal(str(getattr(content, "confidence", "0.5")))
    output = RecommendationOutput(
        correlation_id=correlation_id,
        voyage_id=voyage_id,
        intent=_intent_from_state(state_get("intent_type")),
        summary=summary,
        citations=getattr(content, "citations", []),
        confidence=confidence,
        confidence_level=_confidence_level(confidence),
        fallback_used=getattr(content, "fallback_used", False),
        warnings=state_get("errors", []),
    )
    return RecommendResponse(correlation_id=correlation_id, status="success", output=output)


@app.post("/recommend")
async def recommend(req: RecommendRequest):
    """
    Endpoint utama yang menjalankan keseluruhan graf (Retrieval -> Recommendation).
    """
    correlation_id = req.correlation_id or uuid4()

    # Inisiasi state awal
    initial_state = OrchestratorState(
        request_id=correlation_id,
        query=req.query,
        request_type=req.request_type,
        voyage_id=str(req.voyage_id) if req.voyage_id else None,
        trace=[]
    )
    
    try:
        # Jalankan StateGraph LangGraph (menjalankan aliran dari entry point sampai END)
        final_state = agent_graph.invoke(initial_state)

        return _response_from_final_state(correlation_id, req.voyage_id, final_state).model_dump(
            mode="json"
        )
    except Exception as e:
        error = RecommendResponse(
            correlation_id=correlation_id,
            status="failed",
            errors=[str(e)],
        )
        raise HTTPException(status_code=500, detail=error.model_dump(mode="json"))

@app.get("/health")
async def health_check():
    """Endpoint untuk mengecek apakah orchestrator hidup."""
    return {"status": "healthy", "service": "opticargo-agents"}


@app.get("/health/live")
async def health_live():
    return {"status": "ok", "service": "opticargo-agents"}


@app.get("/health/ready")
async def health_ready():
    return {"status": "ready", "service": "opticargo-agents"}


@app.get("/metrics")
async def metrics():
    return Response(
        "opticargo_agents_up 1\n",
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )
