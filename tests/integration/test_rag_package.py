import os
import pytest

@pytest.mark.skipif(not os.getenv("QDRANT_URL"), reason="QDRANT_URL tidak tersedia untuk live test")
def test_qdrant_live_connection():
    """Memastikan adapter RAG bisa melakukan ping ke server Qdrant."""
    try:
        from opticargo_agents.config import get_settings
        from qdrant_client import QdrantClient
    except ImportError:
        pytest.skip("Dependensi qdrant-client tidak terinstal")

    settings = get_settings()
    url = os.getenv("QDRANT_URL", settings.qdrant_url)
    api_key = os.getenv("QDRANT_API_KEY", None)

    try:
        client = QdrantClient(url=url, api_key=api_key)
        # Mengambil daftar koleksi adalah cara teringan untuk memverifikasi koneksi
        collections = client.get_collections()
        assert collections is not None
    except Exception as e:
        pytest.fail(f"Koneksi live ke Qdrant gagal: {e}")