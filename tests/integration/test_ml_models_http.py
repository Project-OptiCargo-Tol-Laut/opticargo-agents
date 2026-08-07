import os
import pytest

@pytest.mark.skipif(not os.getenv("ML_MODELS_URL"), reason="ML_MODELS_URL tidak diset")
def test_ml_models_live_ping():
    """Memastikan koneksi HTTP ke service ML Models berhasil."""
    try:
        import httpx
    except ImportError:
        pytest.skip("httpx tidak tersedia")
    
    url = os.getenv("ML_MODELS_URL")
    try:
        # Melakukan ping ringan ke root/health
        response = httpx.get(f"{url}/", timeout=5.0)
        # Asalkan bisa nyambung (meski 404 karena rutenya beda), artinya server hidup
        assert response.status_code != 0
    except Exception as e:
        pytest.fail(f"Koneksi live ke ML Models HTTP gagal: {e}")