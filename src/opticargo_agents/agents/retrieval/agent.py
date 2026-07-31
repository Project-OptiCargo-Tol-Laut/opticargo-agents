from opticargo_agents.orchestrator.state import OrchestratorState
from opticargo_shared.agent_state.retrieval import RetrievalAgentOutput
from opticargo_rag_pipeline.retrieve.hybrid_retriever import hybrid_retrieve

def retrieval_node(state: OrchestratorState) -> dict:
    """
    Node untuk agen RAG.
    Melakukan hybrid retrieval menggunakan Qdrant (teks regulasi)
    yang diperkaya dengan konteks spasial/lokasi dari Knowledge Graph.
    """
        # 1. Intip hasil barang yang sudah dipilih oleh agen Optimasi (sebelumnya)
    # Gunakan candidate_labels dari state (disimpan oleh execute_graph_query_node)
    # karena BackhaulCandidate tidak lagi memiliki field commodity_name
    labels = getattr(state, "candidate_labels", [])

    if labels:
        commodity_names = list(set([lb["commodity_name"] for lb in labels]))
        komoditas_str = ", ".join(commodity_names)
        query = f"Persyaratan regulasi, sertifikasi, dan aturan bongkar muat untuk pengiriman komoditas: {komoditas_str}"
    else:
        # Gunakan state.commodity jika ada, atau state.query secara langsung jika ini adalah pertanyaan regulasi
        if state.commodity:
            query = f"Syarat dan regulasi untuk: {state.commodity}"
        else:
            query = state.query
    
    # Ambil konteks graf dari hasil Intent Extraction
    graph_context = {}
    if state.origin_port and state.destination_port:
        graph_context["route"] = f"{state.origin_port} to {state.destination_port}"
    elif state.origin_port:
        graph_context["route"] = state.origin_port
    elif state.voyage_id:
        graph_context["route"] = state.voyage_id
        
    try:
        
        rag_results = hybrid_retrieve(query=query, graph_context=graph_context, top_k=3)
        retrieved_chunks = [
            {"id": chunk.id, "text": chunk.text, "document": chunk.document_name, "score": chunk.score}
            for chunk in rag_results
        ]
        
    except Exception as e:
        print(f"Retrieval Connection Error: {e}")
        # Kembalikan list kosong jika Qdrant tidak menyala
        retrieved_chunks = []
        
    output = RetrievalAgentOutput(
        request_id=state.request_id,
        retrieved_chunks=retrieved_chunks,
        knowledge_graph_context=str(graph_context) if graph_context else None
    )
    
    return {"retrieval_result": output, "trace": state.trace + ["retrieval"]}
