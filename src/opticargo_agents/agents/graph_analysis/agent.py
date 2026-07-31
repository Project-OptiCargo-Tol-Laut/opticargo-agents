"""
graph_analysis/agent.py  (Refactored untuk Self-Correction Loop)

Perubahan dari versi sebelumnya:
- Node ini TIDAK lagi langsung mengeksekusi query ke Neo4j.
- Node ini hanya MEMBANGUN query Cypher berdasarkan state (intent, filters)
  lalu menyimpannya ke state.pending_cypher_query.
- Eksekusi query dilakukan oleh execute_graph_query_node SETELAH
  cypher_validator_node memvalidasi dan mungkin memperbaikinya.
"""

import uuid
from decimal import Decimal
from opticargo_agents.orchestrator.state import OrchestratorState


def graph_analysis_node(state: OrchestratorState) -> dict:
    """
    Node LangGraph: Pembangun Query Cypher.

    Membangun query dan parameter berdasarkan intent dan filter dari state,
    lalu menyimpannya sebagai pending_cypher_query dan pending_cypher_params
    agar bisa divalidasi oleh cypher_validator_node sebelum dieksekusi.
    """
    min_cap = float(state.min_capacity) if state.min_capacity else 0.0

    base_query = """
    MATCH (ship:Ship)-[m:MELAYANI]->(origin:Port)
    MATCH (origin)-[r:TERHUBUNG_DENGAN]->(dest:Port)
    MATCH (sup:Supplier)-[:BERLOKASI_DI]->(origin)
    MATCH (sup)-[:MENYUPLAI]->(com:Commodity)
    """

    where_clauses = ["m.remaining_capacity_ton >= $min_capacity"]
    if state.origin_port:
        where_clauses.append("origin.name CONTAINS $origin_port")
    if state.destination_port:
        where_clauses.append("dest.name CONTAINS $destination_port")
    if state.commodity:
        where_clauses.append("com.name CONTAINS $commodity")

    where_str = " WHERE " + " AND ".join(where_clauses)

    return_str = """
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
    """
    limit_str = " LIMIT 15" if (state.origin_port or state.destination_port) else " LIMIT 10"

    final_query = base_query + where_str + return_str + limit_str

    params = {
        "min_capacity": min_cap,
        "origin_port": state.origin_port or "",
        "destination_port": state.destination_port or "",
        "commodity": state.commodity or "",
    }

    print(f"[GraphAnalysis] Query siap. Filter: origin={state.origin_port}, "
          f"dest={state.destination_port}, commodity={state.commodity}, "
          f"min_cap={min_cap}")

    return {
        "pending_cypher_query": final_query,
        "pending_cypher_params": params,
        "cypher_retry_count": 0,   # Reset counter setiap query baru
        "last_cypher_error": None,
        "trace": state.trace + ["graph_analysis"],
    }
