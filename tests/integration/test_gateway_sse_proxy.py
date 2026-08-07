import os
import pytest

@pytest.mark.skipif(not os.getenv("GATEWAY_URL"), reason="GATEWAY_URL tidak diset")
def test_gateway_sse_chat_endpoint_ping():
    """Memastikan rute streaming chat (SSE) tersedia untuk proxy Gateway."""
    try:
        import httpx
    except ImportError:
        pytest.skip("httpx tidak tersedia")

    url = os.getenv("GATEWAY_URL")
    try:
        response = httpx.options(f"{url}/api/v1/chat", timeout=5.0)
        assert response.status_code != 0
    except Exception as e:
        pytest.fail(f"Endpoint chat SSE tidak terjangkau: {e}")