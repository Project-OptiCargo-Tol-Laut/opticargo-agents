import pytest

def test_dependency_urls_are_configured():
    """Memastikan URL ke Neo4j, Qdrant, dan ML Models bisa dibaca dari konfigurasi."""
    try:
        from opticargo_agents.config import get_settings
    except ImportError:
        pytest.skip("Konfigurasi tidak ditemukan")
        
    settings = get_settings()
    
    # Memastikan URL tidak None, minimal string kosong atau default url
    assert isinstance(settings.neo4j_uri, str)
    assert isinstance(settings.qdrant_url, str)
    assert isinstance(settings.ml_models_internal_url, str)