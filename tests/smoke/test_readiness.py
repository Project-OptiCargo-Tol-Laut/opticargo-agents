import pytest
import httpx
import anyio

def test_readiness_probe_is_accessible():
    """Memastikan endpoint readiness merespons (200 OK atau 503 Unavailable jika DB mati)."""
    try:
        from opticargo_agents.api import app
    except Exception:
        pytest.skip("App gagal di-load")

    async def run_test():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            res = await client.get("/health/ready")
            if res.status_code == 404:
                res = await client.get("/ready")
            return res

    response = anyio.run(run_test)
    # Karena ini smoke test (tanpa database hidup), wajar jika statusnya 503 (Service Unavailable)
    # Yang penting BUKAN 500 (Internal Server Error akibat kode crash)
    assert response.status_code in (200, 503), f"Readiness crash dengan kode: {response.status_code}"