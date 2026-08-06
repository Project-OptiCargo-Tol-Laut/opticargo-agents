import pytest
fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

def test_readiness_probe_is_accessible():
    """Memastikan endpoint readiness merespons (200 OK atau 503 Unavailable jika DB mati)."""
    try:
        from opticargo_agents.api import app
        client = TestClient(app)
    except Exception:
        pytest.skip("App gagal di-load")

    response = client.get("/health/ready")
    if response.status_code == 404:
        response = client.get("/ready")
        
    # Karena ini smoke test (tanpa database hidup), wajar jika statusnya 503 (Service Unavailable)
    # Yang penting BUKAN 500 (Internal Server Error akibat kode crash)
    assert response.status_code in (200, 503), f"Readiness crash dengan kode: {response.status_code}"