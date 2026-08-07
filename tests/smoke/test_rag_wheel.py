import os
import pytest

@pytest.mark.skipif(not os.getenv("TEST_WHEEL_BUILD"), reason="Hanya dijalankan saat validasi hasil wheel build")
def test_rag_wheel_dependencies():
    """Memastikan dependensi RAG (qdrant_client) tidak bocor/hilang saat package di-build."""
    try:
        import qdrant_client
        assert qdrant_client.__version__ is not None
    except ImportError:
        pytest.fail("Dependensi 'qdrant-client' hilang. Pastikan terdaftar di pyproject.toml")