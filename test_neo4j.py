import sys
import os
sys.path.append(os.path.abspath("src"))
from opticargo_knowledge_graph.client import get_session

query = """
MATCH (ship:Ship)-[m:MELAYANI]->(origin:Port)
WHERE origin.name CONTAINS 'Biak'
MATCH (origin)-[r:TERHUBUNG_DENGAN]->(dest:Port)
WHERE dest.name CONTAINS 'Tanjung Perak'
MATCH (sup:Supplier)-[:BERLOKASI_DI]->(origin)
MATCH (sup)-[:MENYUPLAI]->(com:Commodity)
RETURN ship.name, m.remaining_capacity_ton, origin.name, dest.name
"""
try:
    with get_session() as session:
        result = session.run(query)
        for r in result:
            print(r.data())
except Exception as e:
    print(e)
