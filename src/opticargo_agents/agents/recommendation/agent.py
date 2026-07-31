import os
import uuid
from datetime import datetime
from groq import Groq
from opticargo_agents.orchestrator.state import OrchestratorState
from opticargo_shared.agent_state.recommendation_agent import RecommendationAgentOutput
from opticargo_shared.models.recommendation import Recommendation

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
    
    # Format daftar komoditas yang dipilih agar LLM tahu nama barangnya
    cargos_info = "\n".join([f"- {c.commodity_name} dari {c.supplier_name} ({c.volume_ton} ton)" for c in optimized_cargos])
    if not cargos_info:
        cargos_info = "Tidak ada muatan yang ditemukan."
        
    # Format dokumen RAG agar mudah dibaca LLM
    rag_context = ""
    for doc in retrieved_docs:
        rag_context += f"--- Dokumen: {doc.get('document', 'Tidak Diketahui')} ---\n"
        rag_context += f"{doc.get('text', '')}\n\n"
        
    if not rag_context.strip():
        rag_context = "Tidak ada dokumen regulasi yang ditemukan."
        
    if state.intent_type == "GENERAL_CHAT":
        prompt = f"""
        Anda adalah OptiCargo AI, asisten logistik maritim cerdas.
        Jawab sapaan user secara singkat dan ramah (1-2 kalimat saja). Tidak perlu menyebut muatan atau regulasi.
        
        Pertanyaan User: {state.query}
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

    rec = Recommendation(
        id=uuid.uuid4(),
        voyage_id=uuid.UUID(state.voyage_id) if state.voyage_id else uuid.uuid4(),
        recommendation_type="backhaul",
        content={"narrative": narrative},
        score=0.95,
        status="pending",
        generated_at=datetime.utcnow()
    )
    
    output = RecommendationAgentOutput(
        request_id=state.request_id,
        final_recommendation=rec,
        draft_document_paths=[]
    )
    
    return {"final_recommendation": output, "trace": state.trace + ["recommendation"]}
