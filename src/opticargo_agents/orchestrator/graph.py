from langgraph.graph import StateGraph, END
from opticargo_agents.orchestrator.state import OrchestratorState

# Import nodes
from opticargo_agents.agents.retrieval.agent import retrieval_node
from opticargo_agents.agents.graph_analysis.agent import graph_analysis_node
from opticargo_agents.agents.optimization.agent import optimization_node
from opticargo_agents.agents.recommendation.agent import recommendation_node
from opticargo_agents.agents.intent.intent_parser import intent_extraction_node

def route_intent(state: OrchestratorState):
    """Fungsi cabang dinamis penentu arah arsitektur"""
    intent = state.intent_type
    if intent == "REGULATION_QUERY":
        return "retrieval" # Langsung tanya hukum, skip Neo4j
    elif intent == "ROUTE_OPTIMIZATION":
        return "graph_analysis" # Tanya rute muatan, tembak Neo4j
    else:
        return "recommendation" # Pertanyaan sapaan umum, langsung ke LLM akhir

def build_graph():
    graph = StateGraph(OrchestratorState)
    
    # Tambahkan nodes
    graph.add_node("intent_extraction", intent_extraction_node)
    graph.add_node("retrieval", retrieval_node)
    graph.add_node("graph_analysis", graph_analysis_node)
    graph.add_node("optimization", optimization_node)
    graph.add_node("recommendation", recommendation_node)

    # Susun alur tepi (Edges)
    graph.set_entry_point("intent_extraction")
    
    # 1. Routing Dinamis Berdasarkan Intent
    graph.add_conditional_edges(
        "intent_extraction",
        route_intent,
        {
            "retrieval": "retrieval",
            "graph_analysis": "graph_analysis",
            "recommendation": "recommendation"
        }
    )
    
    # 2. Alur jika masuk ke Rute Optimasi
    graph.add_edge("graph_analysis", "optimization")
    graph.add_edge("optimization", "retrieval")
    
    # 3. Semua agen pada akhirnya akan berkumpul di Recommendation (LLM Penjawab)
    graph.add_edge("retrieval", "recommendation")
    
    # 4. Selesai
    graph.add_edge("recommendation", END)
    
    return graph.compile()