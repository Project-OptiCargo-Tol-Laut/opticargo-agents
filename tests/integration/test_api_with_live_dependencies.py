import os
import pytest

@pytest.mark.skipif(not os.getenv("LIVE_API_URL"), reason="LIVE_API_URL tidak diset")
def test_live_api_health():
    """Memastikan API utama merespons jika dijalankan dengan dependensi live."""
    try:
        import httpx
    except ImportError:
        pytest.skip("httpx tidak tersedia")

    url = os.getenv("LIVE_API_URL")
    try:
        response = httpx.get(f"{url}/health/live", timeout=5.0)
        assert response.status_code in (200, 204), "API live gagal merespons liveness probe"
    except Exception as e:
        pytest.fail(f"Koneksi ke API Live gagal: {e}")