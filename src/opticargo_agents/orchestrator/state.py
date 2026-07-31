from typing import Optional, List, Dict, Any
from opticargo_shared.agent_state.base import BaseAgentState
from opticargo_shared.agent_state.graph_analysis import GraphAnalysisOutput
from opticargo_shared.agent_state.optimization import OptimizationOutput
from opticargo_shared.agent_state.recommendation_agent import RecommendationAgentOutput
from opticargo_shared.agent_state.retrieval import RetrievalAgentOutput

class OrchestratorState(BaseAgentState):
    """
    State yang mengalir sepanjang eksekusi LangGraph.
    Membungkus output dari masing-masing agen agar bisa saling digunakan.
    """
    # Request Info
    request_type: str = "general" 
    query: str = ""
    voyage_id: Optional[str] = None
    
    intent_type: str = "GENERAL_CHAT" 
    commodity: Optional[str] = None
    min_capacity: Optional[float] = None
    
    origin_port: Optional[str] = None
    destination_port: Optional[str] = None
    
    # Agent Outputs
    retrieval_result: Optional[RetrievalAgentOutput] = None
    graph_analysis_result: Optional[GraphAnalysisOutput] = None
    optimization_result: Optional[OptimizationOutput] = None
    final_recommendation: Optional[RecommendationAgentOutput] = None
    
    trace: List[str] = []
