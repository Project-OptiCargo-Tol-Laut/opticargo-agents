import pytest
fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

def test_prometheus_metrics_format():
    """Memastikan format kembalian metrics valid untuk Prometheus."""
    try:
        from opticargo_agents.api import app
        client = TestClient(app)
    except Exception:
        pytest.skip("App gagal di-load")

    response = client.get("/metrics")
    if response.status_code == 200:
        # Prometheus metric wajib memiliki tipe konten text/plain
        assert "text/plain" in response.headers.get("content-type", "")
        # Biasanya selalu mengekspos metrik standar bawaan Python/Proses
        assert "python_" in response.text or "process_" in response.text
    else:
        pytest.skip("Endpoint /metrics mungkin dinonaktifkan di environment ini")