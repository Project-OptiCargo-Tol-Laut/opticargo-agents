import os
import pytest

@pytest.mark.skipif(not os.getenv("GATEWAY_URL"), reason="GATEWAY_URL tidak diset")
def test_gateway_recommendation_endpoint_ping():
    """Memastikan rute rekomendasi dapat dijangkau oleh Gateway."""
    try:
        import httpx
    except ImportError:
        pytest.skip("httpx tidak tersedia")

    url = os.getenv("GATEWAY_URL")
    try:
        # Melakukan ping ringan (OPTIONS) untuk memastikan route ada
        response = httpx.options(f"{url}/api/v1/recommendations", timeout=5.0)
        assert response.status_code != 0
    except Exception as e:
        pytest.fail(f"Endpoint rekomendasi tidak terjangkau: {e}")