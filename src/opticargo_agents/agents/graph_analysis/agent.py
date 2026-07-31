from opticargo_agents.orchestrator.state import OrchestratorState
from opticargo_shared.agent_state.graph_analysis import GraphAnalysisOutput, BackhaulCandidate
from opticargo_knowledge_graph.client import get_session
from opticargo_knowledge_graph.queries.backhaul_discovery import find_backhaul_candidates
import uuid
from decimal import Decimal

def graph_analysis_node(state: OrchestratorState) -> dict:
    """
    Node untuk agen Analisis Graf.
    Menerima state, melakukan query graf via opticargo_knowledge_graph
    untuk mencari peluang muatan balik (backhaul candidates).
    """
    candidates_data = []
    
    try:
        with get_session() as session:
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
            limit_str = " LIMIT 15" if state.origin_port or state.destination_port else " LIMIT 10"
            
            final_query = base_query + where_str + return_str + limit_str
            
            params = {
                "min_capacity": min_cap,
                "origin_port": state.origin_port or "",
                "destination_port": state.destination_port or ""
            }
            
            result = session.run(final_query, params)
            raw_candidates = [record.data() for record in result]
            
            # Map hasil Cypher ke schema Pydantic opticargo-shared
            for row in raw_candidates:
                volume = row.get('supplier_volume')
                if volume is None:
                    volume = 100
                candidates_data.append(
                    BackhaulCandidate(
                        supplier_id=uuid.uuid4(),
                        commodity_id=uuid.uuid4(),
                        commodity_name=row.get('commodity_name', 'Unknown Commodity'),
                        supplier_name=row.get('supplier_name', 'Unknown Supplier'),
                        volume_ton=Decimal(str(volume)),
                        match_score=0.85
                    )
                )
    except Exception as e:
        print(f"Graph Connection Error: {e}")
        candidates_data = []

    output = GraphAnalysisOutput(
        request_id=state.request_id,
        candidates=candidates_data
    )
    
    return {"graph_analysis_result": output, "trace": state.trace + ["graph_analysis"]}
