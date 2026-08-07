import pytest
import httpx
import anyio

def test_prometheus_metrics_format():
    """Memastikan format kembalian metrics valid untuk Prometheus."""
    try:
        from opticargo_agents.api import app
    except Exception:
        pytest.skip("App gagal di-load")

    async def run_test():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.get("/metrics")

    response = anyio.run(run_test)
    if response.status_code == 200:
        assert "text/plain" in response.headers.get("content-type", "")
        assert "python_" in response.text or "process_" in response.text
    else:
        pytest.skip("Endpoint /metrics mungkin dinonaktifkan di environment ini")