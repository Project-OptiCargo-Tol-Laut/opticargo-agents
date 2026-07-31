"""
execute_graph_query/agent.py

Node eksekutor query ke Neo4j.
Node ini dijalankan SETELAH cypher_validator_node berhasil memvalidasi
(dan mungkin memperbaiki) query Cypher.

Ia mengambil state.validated_cypher dan state.pending_cypher_params,
mengeksekusinya ke Neo4j, lalu memetakan hasilnya ke schema Pydantic
GraphAnalysisOutput dari opticargo-shared.
"""

import uuid
from decimal import Decimal

from opticargo_agents.orchestrator.state import OrchestratorState
from opticargo_shared.agent_state.graph_analysis import GraphAnalysisOutput, BackhaulCandidate
from opticargo_knowledge_graph.client import get_session


def execute_graph_query_node(state: OrchestratorState) -> dict:
    """
    Node LangGraph: Eksekutor Query Neo4j.

    Mengambil validated_cypher dari state (sudah diverifikasi oleh validator),
    mengeksekusinya, dan memetakan hasilnya ke GraphAnalysisOutput.
    """
    validated_query = getattr(state, "validated_cypher", None)
    params = getattr(state, "pending_cypher_params", {})

    candidates_data = []
    _candidate_labels = []   # Metadata nama untuk narasi rekomendasi

    if not validated_query:
        print("[ExecuteGraphQuery] Tidak ada validated_cypher, output kosong.")
        output = GraphAnalysisOutput(
            request_id=state.request_id,
            candidates=[]
        )
        return {"graph_analysis_result": output, "trace": state.trace + ["execute_graph_query"]}

    # Log apakah ini hasil koreksi atau query original
    retry_count = state.cypher_retry_count
    if retry_count > 0:
        print(f"[ExecuteGraphQuery] 🔄 Mengeksekusi query yang telah dikoreksi "
              f"({retry_count}x retry).")
    else:
        print("[ExecuteGraphQuery] ✅ Mengeksekusi query original yang valid.")

    try:
        with get_session() as session:
            result = session.run(validated_query, params)
            raw_candidates = [record.data() for record in result]

            print(f"[ExecuteGraphQuery] Ditemukan {len(raw_candidates)} kandidat dari Neo4j.")

            for row in raw_candidates:
                volume = row.get("supplier_volume")
                if volume is None:
                    volume = 100

                # BackhaulCandidate di opticargo-shared tidak menyimpan nama teks,
                # hanya ID dan angka. Info nama kita simpan ke list terpisah untuk
                # digunakan oleh recommendation prompt.
                candidates_data.append(
                    BackhaulCandidate(
                        supplier_id=uuid.uuid4(),
                        commodity_id=uuid.uuid4(),
                        volume_ton=Decimal(str(volume)),
                        match_score=0.85,
                    )
                )

                # Simpan nama lengkap untuk narasi rekomendasi
                _candidate_labels.append({
                    "commodity_name": row.get("commodity_name", "Unknown Commodity"),
                    "supplier_name":  row.get("supplier_name",  "Unknown Supplier"),
                    "volume_ton":     volume,
                    "origin":         row.get("origin_port", ""),
                    "destination":    row.get("destination_port", ""),
                })

    except Exception as e:
        # Seharusnya tidak terjadi karena query sudah divalidasi,
        # tapi kita tetap tangkap untuk keamanan
        print(f"[ExecuteGraphQuery] ❌ Error saat eksekusi: {e}")
        candidates_data = []

    output = GraphAnalysisOutput(
        request_id=state.request_id,
        candidates=candidates_data
    )

    return {
        "graph_analysis_result": output,
        "candidate_labels":      _candidate_labels,  # untuk narasi recommendation
        "trace": state.trace + ["execute_graph_query"],
    }
