import os
import uuid
from datetime import datetime
from groq import Groq
from opticargo_agents.orchestrator.state import OrchestratorState
from opticargo_shared.agent_state.recommendation_agent import RecommendationAgentOutput
from opticargo_shared.models.recommendation import Recommendation, RecommendationContent
from opticargo_shared.agent_state.candidates import ScoreBreakdown
from opticargo_shared.enums import ModelMode
from datetime import timezone

def recommendation_node(state: OrchestratorState) -> dict:
    """
    Node untuk agen Rekomendasi (Sintesis Akhir).
    Memanggil LLM (Groq Llama-3) untuk menyusun output dari agen-agen 
    sebelumnya menjadi narasi logistik yang profesional.
    """
    # 1. Kumpulkan Konteks dari Agent Sebelumnya
    retrieved_docs = state.retrieval_result.retrieved_chunks if state.retrieval_result else []
    optimized_cargos = state.optimization_result.selected_candidates if state.optimization_result else []
    est_revenue = state.optimization_result.estimated_total_revenue if state.optimization_result else 0
    
    # Gunakan candidate_labels (nama lengkap) yang disimpan oleh execute_graph_query_node
    # karena BackhaulCandidate di opticargo-shared sudah tidak menyimpan nama teks
    labels = getattr(state, "candidate_labels", [])
    if labels:
        cargos_info = "\n".join([
            f"- {lb['commodity_name']} dari {lb['supplier_name']} ({lb['volume_ton']} ton)"
            for lb in labels
        ])
    else:
        cargos_info = "Tidak ada muatan yang ditemukan."
        
    # Format dokumen RAG agar mudah dibaca LLM
    rag_context = ""
    for doc in retrieved_docs:
        rag_context += f"--- Dokumen: {doc.get('document', 'Tidak Diketahui')} ---\n"
        rag_context += f"{doc.get('text', '')}\n\n"
        
    if not rag_context.strip():
        rag_context = "Tidak ada dokumen regulasi yang ditemukan."
        
    if state.intent_type == "OUT_OF_SCOPE":
        # Langsung kembalikan tanpa memanggil LLM sama sekali
        narrative = (
            "Maaf, saya adalah OptiCargo AI yang khusus menangani logistik maritim. "
            "Saya hanya dapat membantu pertanyaan seputar muatan kapal, rute pelayaran, "
            "dan regulasi pengiriman laut. Ada yang bisa saya bantu di bidang tersebut?"
        )
    elif state.intent_type == "GENERAL_CHAT":
        prompt = f"""
        Anda adalah OptiCargo AI, asisten logistik maritim Indonesia.
        Tugas Anda HANYA membantu hal yang berkaitan dengan logistik, maritim, kapal, muatan, dan pelabuhan.
        
        Pertanyaan User: {state.query}
        
        Instruksi:
        - Jawab hanya jika pertanyaan berkaitan dengan logistik/maritim (sapaan, pertanyaan umum tentang sistem, dll).
        - Jawab singkat dan ramah (1-2 kalimat).
        - JANGAN menjawab pertanyaan yang tidak berhubungan dengan logistik maritim.
        """
    elif state.intent_type == "REGULATION_QUERY":
        prompt = f"""
        Anda adalah OptiCargo AI, asisten logistik maritim cerdas.
        Jawab pertanyaan regulasi berikut secara spesifik dan akurat berdasarkan dokumen regulasi yang diberikan.
        
        Pertanyaan User: {state.query}
        
        Dokumen Regulasi Relevan:
        {rag_context}
        
        Instruksi:
        - Jawab langsung ke intinya berdasarkan dokumen di atas.
        - Sebutkan nama dokumen aslinya saat mengutip aturan.
        - JANGAN membahas muatan balik (backhaul), estimasi pendapatan, atau merekomendasikan komoditas.
        """
    else:
        prompt = f"""
        Anda adalah OptiCargo AI, asisten logistik maritim cerdas.
        Berdasarkan data berikut, buatkan rekomendasi muatan balik (backhaul) yang singkat, padat, dan profesional.
        
        Pertanyaan User: {state.query}
        
        Dokumen Regulasi Relevan:
        {rag_context}
        
        Muatan Terpilih (Hasil Optimasi):
        {cargos_info}
        Estimasi Pendapatan Tambahan: Rp {est_revenue:,.2f}
        
        Buatlah jawaban dalam 2 paragraf:
        1. Rekomendasi muatan yang harus diambil (sebutkan komoditas dan supplier-nya jika ada) dan potensi pendapatannya. Jika tidak ada muatan, sampaikan dengan sopan.
        2. Peringatan regulasi penting berdasarkan dokumen di atas yang terkait dengan komoditas tersebut. Sebutkan nama dokumen aslinya!
        """

    api_key = os.getenv("GROQ_API_KEY")

    # OUT_OF_SCOPE: narrative sudah di-set di atas, skip pemanggilan LLM
    if state.intent_type != "OUT_OF_SCOPE":
        narrative = ""
        if api_key:
            try:
                client = Groq(api_key=api_key)
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    temperature=0.3
                )
                narrative = response.choices[0].message.content
            except Exception as e:
                print(f"Groq API Error: {e}")
                narrative = f"Error memanggil LLM (Groq). Detail: {e}"
        else:
            narrative = "Error: GROQ_API_KEY belum dikonfigurasi."

    rec_content = RecommendationContent(
        summary=narrative,
        score_breakdown=ScoreBreakdown(
            total_score=0.95,
            economic_value=0.9,
            schedule_fit=1.0,
            capacity_fit=1.0,
            distance_fit=1.0,
            risk_score=0.1,
            model_mode=ModelMode.heuristic
        ),
        confidence=0.95,
        recommended_human_action="Review and approve recommendation."
    )

    rec = Recommendation(
        id=uuid.uuid4(),
        voyage_id=uuid.UUID(state.voyage_id) if state.voyage_id else uuid.uuid4(),
        recommendation_type="backhaul",
        content=rec_content,
        score=0.95,
        status="pending",
        generated_at=datetime.now(timezone.utc),
        trace_id=uuid.uuid4()
    )
    
    output = RecommendationAgentOutput(
        request_id=state.request_id,
        final_recommendation=rec,
        draft_document_paths=[]
    )
    
    return {"final_recommendation": output, "trace": state.trace + ["recommendation"]}
