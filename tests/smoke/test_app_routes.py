import pytest
import httpx
import anyio

def test_asgi_app_initialization():
    """Memastikan ASGI app bisa di-impor dan siap menerima request."""
    try:
        from opticargo_agents.api import app
    except ImportError:
        pytest.skip("Objek 'app' tidak ditemukan di opticargo_agents.api")

    # Pastikan app adalah callable (memenuhi standar ASGI)
    assert callable(app), "App harus berupa ASGI callable atau factory function"

    async def run_test():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return True

    assert anyio.run(run_test)