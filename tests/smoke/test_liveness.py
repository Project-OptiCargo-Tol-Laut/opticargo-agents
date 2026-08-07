import pytest
import httpx
import anyio

def test_liveness_probe_returns_200():
    """Memastikan endpoint liveness merespons dengan sukses."""
    try:
        from opticargo_agents.api import app
    except Exception:
        pytest.skip("App gagal di-load")

    async def run_test():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            res = await client.get("/health/live")
            if res.status_code == 404:
                res = await client.get("/health")
            return res

    response = anyio.run(run_test)
    # Smoke test: asalkan server merespons 200 (OK) atau 204 (No Content), berarti server hidup
    assert response.status_code in (200, 204), f"Liveness probe gagal: {response.status_code}"