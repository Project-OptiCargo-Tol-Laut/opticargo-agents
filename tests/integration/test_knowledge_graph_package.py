import os
import pytest

# Melewati tes ini jika tidak ada environment variable NEO4J_URI yang aktif
@pytest.mark.skipif(not os.getenv("NEO4J_URI"), reason="NEO4J_URI tidak tersedia untuk live test")
def test_knowledge_graph_live_connection():
    """Memastikan adapter Knowledge Graph bisa melakukan ping ke database live."""
    try:
        from opticargo_agents.config import get_settings
        from neo4j import GraphDatabase
    except ImportError:
        pytest.skip("Dependensi neo4j tidak terinstal")
        
    settings = get_settings()
    
    # Gunakan URI dari environment, tapi fallback ke setting default jika ada
    uri = os.getenv("NEO4J_URI", settings.neo4j_uri)
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    try:
        # verify_connectivity akan melempar exception jika gagal terhubung
        driver.verify_connectivity()
        assert True
    except Exception as e:
        pytest.fail(f"Koneksi live ke Knowledge Graph gagal: {e}")
    finally:
        driver.close()