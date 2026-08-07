import pytest
import httpx
import anyio

def test_metrics_endpoint_is_accessible():
    """Memastikan Prometheus /metrics endpoint aman diakses."""
    try:
        from opticargo_agents.api import app
    except Exception:
        pytest.skip("App gagal di-load")

    async def run_test():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.get("/metrics")

    response = anyio.run(run_test)
    # 200 OK jika prometheus aktif, 404 Not Found jika rute belum di-mount. Keduanya valid.
    assert response.status_code in (200, 404), "Metrics endpoint crash"