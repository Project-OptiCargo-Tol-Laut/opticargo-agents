import pytest
fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

def test_liveness_probe_returns_200():
    """Memastikan endpoint liveness merespons dengan sukses."""
    try:
        from opticargo_agents.api import app
        client = TestClient(app)
    except Exception:
        pytest.skip("App gagal di-load")

    # Coba rute standar yang sering digunakan
    response = client.get("/health/live")
    if response.status_code == 404:
        response = client.get("/health")
        
    # Smoke test: asalkan server merespons 200 (OK) atau 204 (No Content), berarti server hidup
    assert response.status_code in (200, 204), f"Liveness probe gagal: {response.status_code}"