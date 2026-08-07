import os
import pytest

@pytest.mark.skipif(not os.getenv("TEST_WHEEL_BUILD"), reason="Hanya dijalankan saat validasi hasil wheel build")
def test_knowledge_graph_wheel_dependencies():
    """Memastikan dependensi knowledge graph (neo4j) tidak bocor/hilang saat package di-build."""
    try:
        import neo4j
        assert neo4j.__version__ is not None
    except ImportError:
        pytest.fail("Dependensi 'neo4j' hilang. Pastikan terdaftar di pyproject.toml")