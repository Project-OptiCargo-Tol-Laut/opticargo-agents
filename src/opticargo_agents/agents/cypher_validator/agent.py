"""
cypher_validator/agent.py

Node Self-Correction Loop untuk OptiCargo AI.

Cara kerja:
1. Terima query Cypher dari graph_analysis_node (via state)
2. Jalankan EXPLAIN di Neo4j — hanya cek sintaks, tidak eksekusi data
3. Jika VALID  → set state.cypher_validated = True, lanjut eksekusi
4. Jika ERROR  → kirim pesan error + Graph Schema ke LLM untuk diperbaiki
5. Retry maksimal MAX_RETRIES kali. Jika tetap gagal → gunakan FALLBACK query.
"""

import os
from groq import Groq
from opticargo_agents.orchestrator.state import OrchestratorState
from opticargo_knowledge_graph.client import get_session

# ─── Konfigurasi ────────────────────────────────────────────────────────────
MAX_RETRIES = 3

# Schema singkat Neo4j kita — ini yang dikirim ke LLM saat terjadi error
# agar LLM tahu nama relasi dan properti yang benar
GRAPH_SCHEMA = """
Node Labels dan Propertinya:
  - Ship       : {name, deadweight_tonnage}
  - Port       : {name, code}
  - Supplier   : {business_name, avg_monthly_volume_ton, rating, verified}
  - Commodity  : {name, category, is_perishable}

Relationship Types:
  - (Ship)-[:MELAYANI]->(Port)              : {remaining_capacity_ton}
  - (Port)-[:TERHUBUNG_DENGAN]->(Port)      : {distance_nm, tarif_general_cargo_idr,
                                               tarif_dry_container_idr, tarif_reefer_container_idr}
  - (Supplier)-[:BERLOKASI_DI]->(Port)
  - (Supplier)-[:MENYUPLAI]->(Commodity)
"""

# Fallback query yang sudah PASTI benar — digunakan jika LLM gagal koreksi 3x
FALLBACK_QUERY = """
MATCH (ship:Ship)-[m:MELAYANI]->(origin:Port)
MATCH (origin)-[r:TERHUBUNG_DENGAN]->(dest:Port)
MATCH (sup:Supplier)-[:BERLOKASI_DI]->(origin)
MATCH (sup)-[:MENYUPLAI]->(com:Commodity)
WHERE m.remaining_capacity_ton >= 0
RETURN ship.name AS ship_name,
       ship.deadweight_tonnage AS ship_dw,
       origin.name AS origin_port,
       dest.name AS destination_port,
       m.remaining_capacity_ton AS available_capacity,
       r.distance_nm AS distance_nm,
       r.tarif_general_cargo_idr AS tarif_general,
       r.tarif_dry_container_idr AS tarif_dry,
       r.tarif_reefer_container_idr AS tarif_reefer,
       sup.business_name AS supplier_name,
       sup.avg_monthly_volume_ton AS supplier_volume,
       sup.rating AS supplier_rating,
       sup.verified AS supplier_verified,
       com.name AS commodity_name,
       com.is_perishable AS is_perishable,
       com.category AS commodity_category
ORDER BY m.remaining_capacity_ton DESC
LIMIT 10
"""


def _validate_cypher(session, query: str, params: dict) -> tuple[bool, str]:
    """
    Jalankan EXPLAIN di Neo4j untuk memvalidasi sintaks query.
    Mengembalikan (is_valid: bool, error_message: str).
    EXPLAIN hanya menganalisis query plan — tidak membaca atau menulis data.
    """
    try:
        explain_query = f"EXPLAIN {query}"
        session.run(explain_query, params)
        return True, ""
    except Exception as e:
        return False, str(e)


def _repair_cypher_with_llm(original_query: str, error_message: str, retry_count: int) -> str:
    """
    Kirim query yang salah + pesan error + schema ke LLM untuk diperbaiki.
    Mengembalikan query yang sudah dikoreksi.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("[CypherValidator] GROQ_API_KEY tidak ditemukan, menggunakan fallback.")
        return FALLBACK_QUERY

    prompt = f"""Anda adalah ahli Neo4j Cypher. Query berikut menghasilkan error.
Perbaiki query agar valid sesuai dengan schema yang diberikan.

=== QUERY YANG SALAH ===
{original_query}

=== PESAN ERROR DARI NEO4J ===
{error_message}

=== SCHEMA GRAPH YANG BENAR ===
{GRAPH_SCHEMA}

=== INSTRUKSI ===
- Kembalikan HANYA query Cypher yang sudah diperbaiki, tanpa penjelasan tambahan.
- Jangan gunakan label, relasi, atau properti yang tidak ada di schema.
- Jaga agar parameter ($min_capacity, $origin_port, $destination_port) tetap ada.
- Ini percobaan ke-{retry_count + 1} dari {MAX_RETRIES}.
"""
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.1,  # Rendah agar deterministik, bukan kreatif
        )
        repaired = response.choices[0].message.content.strip()
        # Bersihkan jika LLM menambahkan markdown code block
        repaired = repaired.replace("```cypher", "").replace("```", "").strip()
        return repaired
    except Exception as e:
        print(f"[CypherValidator] LLM repair error: {e}")
        return FALLBACK_QUERY


def cypher_validator_node(state: OrchestratorState) -> dict:
    """
    Node LangGraph: Self-Correction Loop.

    Node ini menerima query yang sudah disiapkan oleh graph_analysis_node
    (disimpan di state.pending_cypher_query), lalu memvalidasi dan
    memperbaikinya jika diperlukan sebelum dieksekusi.

    Return dict berisi:
      - validated_cypher   : query final yang siap dieksekusi
      - cypher_retry_count : berapa kali sudah retry
      - last_cypher_error  : error terakhir (None jika sukses)
    """
    pending_query = getattr(state, "pending_cypher_query", None)
    params = getattr(state, "pending_cypher_params", {})

    if not pending_query:
        print("[CypherValidator] Tidak ada pending query, skip validasi.")
        return {"validated_cypher": FALLBACK_QUERY, "cypher_retry_count": 0}

    current_query = pending_query
    retry_count = state.cypher_retry_count

    with get_session() as session:
        while retry_count < MAX_RETRIES:
            is_valid, error_msg = _validate_cypher(session, current_query, params)

            if is_valid:
                print(f"[CypherValidator] ✅ Query valid setelah {retry_count} percobaan.")
                return {
                    "validated_cypher": current_query,
                    "cypher_retry_count": retry_count,
                    "last_cypher_error": None,
                }

            print(f"[CypherValidator] ❌ Error percobaan {retry_count + 1}: {error_msg[:80]}...")
            current_query = _repair_cypher_with_llm(current_query, error_msg, retry_count)
            retry_count += 1

    # Jika sudah 3x tetap gagal → gunakan fallback
    print(f"[CypherValidator] ⚠️ Semua percobaan gagal. Menggunakan FALLBACK query.")
    return {
        "validated_cypher": FALLBACK_QUERY,
        "cypher_retry_count": retry_count,
        "last_cypher_error": f"Max retries ({MAX_RETRIES}) tercapai. Fallback digunakan.",
    }
