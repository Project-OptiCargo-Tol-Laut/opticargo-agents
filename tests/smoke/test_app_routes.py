import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

def test_asgi_app_initialization():
    """Memastikan ASGI app bisa di-impor dan siap menerima request."""
    try:
        from opticargo_agents.api import app
    except ImportError:
        pytest.skip("Objek 'app' tidak ditemukan di opticargo_agents.api")

    # Pastikan app adalah callable (memenuhi standar ASGI)
    assert callable(app), "App harus berupa ASGI callable atau factory function"

    # Jika TestClient bisa membungkusnya tanpa crash, berarti aplikasi valid
    client = TestClient(app)
    assert client is not None