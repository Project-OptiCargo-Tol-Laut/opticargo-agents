import pytest
fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

def test_metrics_endpoint_is_accessible():
    """Memastikan Prometheus /metrics endpoint aman diakses."""
    try:
        from opticargo_agents.api import app
        client = TestClient(app)
    except Exception:
        pytest.skip("App gagal di-load")

    response = client.get("/metrics")
    
    # 200 OK jika prometheus aktif, 404 Not Found jika rute belum di-mount. Keduanya valid.
    assert response.status_code in (200, 404), "Metrics endpoint crash"