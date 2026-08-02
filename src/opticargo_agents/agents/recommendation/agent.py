import os
import uuid
from datetime import datetime
from decimal import Decimal
from groq import Groq
from opticargo_agents.orchestrator.state import OrchestratorState
from opticargo_shared.agent_state.citation import Citation
from opticargo_shared.agent_state.recommendation_agent import RecommendationAgentOutput
from opticargo_shared.models.recommendation import Recommendation, RecommendationContent
from opticargo_shared.agent_state.candidates import ScoreBreakdown
from opticargo_shared.enums import ModelMode
from datetime import timezone


def _fallback_narrative(state: OrchestratorState, cargos_info: str, est_revenue) -> str:
    if state.intent_type == "GENERAL_CHAT":
        return (
            "Halo, saya OptiCargo AI. Saya bisa membantu membaca konteks regulasi, "
            "mencari peluang muatan balik, dan merangkum rekomendasi operasional maritim."
        )
    if state.intent_type == "REGULATION_QUERY":
        return (
            "Saya sudah menerima pertanyaan regulasi Anda. Untuk jawaban final berbasis bahasa alami, "
            "konfigurasikan LLM_API_KEY/GROQ_API_KEY; sementara pipeline RAG dan collection Qdrant sudah siap diuji."
        )
    return (
        "Rekomendasi awal berhasil dibuat dengan fallback lokal. "
        f"Muatan kandidat: {cargos_info} Estimasi pendapatan tambahan: Rp {Decimal(str(est_revenue)):,.2f}. "
        "Aktifkan LLM_API_KEY/GROQ_API_KEY untuk narasi final yang lebih lengkap."
    )


def _citations_from_retrieved_docs(retrieved_docs: list[dict]) -> list[Citation]:
    citations: list[Citation] = []
    seen_chunk_ids: set[str] = set()
    for doc in retrieved_docs:
        chunk_id = doc.get("id")
        chunk_key = str(chunk_id)
        if not chunk_id or chunk_key in seen_chunk_ids:
            continue
        seen_chunk_ids.add(chunk_key)

        title = str(doc.get("document") or "Dokumen OptiCargo")
        excerpt = str(doc.get("text") or "").strip()
        citations.append(
            Citation(
                document_id=uuid.uuid5(uuid.NAMESPACE_URL, title),
                chunk_id=uuid.UUID(chunk_key),
                title=title,
                excerpt=excerpt[:500] if excerpt else None,
                score=doc.get("score"),
            )
        )
    return citations


def recommendation_node(state: OrchestratorState) -> dict:
    """
    Node untuk agen Rekomendasi (Sintesis Akhir).
    Memanggil LLM (Groq Llama-3) untuk menyusun output dari agen-agen 
    sebelumnya menjadi narasi logistik yang profesional.
    """
    # 1. Kumpulkan Konteks dari Agent Sebelumnya
    retrieved_docs = state.retrieval_result.retrieved_chunks if state.retrieval_result else []
    citations = _citations_from_retrieved_docs(retrieved_docs)
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

    api_key = os.getenv("LLM_API_KEY") or os.getenv("GROQ_API_KEY")
    fallback_used = not bool(api_key)

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
                fallback_used = False
            except Exception as e:
                print(f"Groq API Error: {e}")
                narrative = f"Error memanggil LLM (Groq). Detail: {e}"
                fallback_used = True
        else:
            narrative = _fallback_narrative(state, cargos_info, est_revenue)

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
        citations=citations,
        confidence=0.95,
        fallback_used=fallback_used,
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
