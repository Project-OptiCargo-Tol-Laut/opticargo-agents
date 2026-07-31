"""
orchestrator/graph.py

Alur LangGraph OptiCargo AI dengan Self-Correction Loop.

Alur ROUTE_OPTIMIZATION (sebelumnya):
  graph_analysis → optimization → retrieval → recommendation

Alur ROUTE_OPTIMIZATION (sekarang, dengan Self-Correction):
  graph_analysis → cypher_validator → execute_graph_query → optimization → retrieval → recommendation

graph_analysis     : Membangun query Cypher (tidak eksekusi)
cypher_validator   : Validasi via EXPLAIN, perbaiki via LLM jika error (max 3x)
execute_graph_query: Eksekusi query yang sudah valid ke Neo4j
"""

from langgraph.graph import StateGraph, END
from opticargo_agents.orchestrator.state import OrchestratorState

# Import nodes
from opticargo_agents.agents.retrieval.agent import retrieval_node
from opticargo_agents.agents.graph_analysis.agent import graph_analysis_node
from opticargo_agents.agents.cypher_validator.agent import cypher_validator_node
from opticargo_agents.agents.execute_graph_query.agent import execute_graph_query_node
from opticargo_agents.agents.optimization.agent import optimization_node
from opticargo_agents.agents.recommendation.agent import recommendation_node
from opticargo_agents.agents.intent.intent_parser import intent_extraction_node


def route_intent(state: OrchestratorState):
    """Fungsi cabang dinamis penentu arah arsitektur berdasarkan intent."""
    intent = state.intent_type
    if intent == "REGULATION_QUERY":
        return "retrieval"         # Langsung tanya Qdrant, skip Neo4j
    elif intent == "ROUTE_OPTIMIZATION":
        return "graph_analysis"    # Masuk pipeline Self-Correction Loop
    elif intent == "OUT_OF_SCOPE":
        return "recommendation"    # Tolak dengan sopan, skip semua pipeline
    else:
        return "recommendation"    # GENERAL_CHAT: sapaan umum, langsung ke LLM akhir


def build_graph():
    graph = StateGraph(OrchestratorState)

    # ── Daftarkan semua nodes ──────────────────────────────────────────────
    graph.add_node("intent_extraction",   intent_extraction_node)
    graph.add_node("retrieval",           retrieval_node)
    graph.add_node("graph_analysis",      graph_analysis_node)
    graph.add_node("cypher_validator",    cypher_validator_node)    # ← BARU
    graph.add_node("execute_graph_query", execute_graph_query_node) # ← BARU
    graph.add_node("optimization",        optimization_node)
    graph.add_node("recommendation",      recommendation_node)

    # ── Entry point ───────────────────────────────────────────────────────
    graph.set_entry_point("intent_extraction")

    # ── 1. Routing Dinamis Berdasarkan Intent ─────────────────────────────
    graph.add_conditional_edges(
        "intent_extraction",
        route_intent,
        {
            "retrieval":      "retrieval",
            "graph_analysis": "graph_analysis",
            "recommendation": "recommendation",
        }
    )

    # ── 2. Self-Correction Pipeline (ROUTE_OPTIMIZATION) ─────────────────
    #   graph_analysis → cypher_validator → execute_graph_query → optimization
    graph.add_edge("graph_analysis",      "cypher_validator")
    graph.add_edge("cypher_validator",    "execute_graph_query")
    graph.add_edge("execute_graph_query", "optimization")
    graph.add_edge("optimization",        "retrieval")

    # ── 3. Semua jalur berkumpul di Recommendation ────────────────────────
    graph.add_edge("retrieval", "recommendation")

    # ── 4. Selesai ────────────────────────────────────────────────────────
    graph.add_edge("recommendation", END)

    return graph.compile()