"""Security: pastikan tidak ada endpoint dokumentasi/OpenAPI publik
(`/docs`, `/openapi.json`, `/redoc`) yang terekspos oleh service internal
ini -- terlepas dari nilai `Settings.enable_openapi`, karena runtime ASGI
saat ini tidak mengimplementasikan generator dokumentasi sama sekali.

Kalau suatu saat OpenAPI docs benar-benar diimplementasikan, test ini harus
diperbarui untuk memverifikasi docs itu hanya dapat diakses secara internal
(bukan menghapus proteksinya).

Rujukan: docs/SECURITY_BOUNDARY.md
"""

import anyio
import httpx

from opticargo_agents.api import app


def _get(path: str) -> httpx.Response:
    async def run_test():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.get(path)

    return anyio.run(run_test)


def test_openapi_json_is_not_publicly_exposed() -> None:
    assert _get("/openapi.json").status_code == 404


def test_swagger_docs_is_not_publicly_exposed() -> None:
    assert _get("/docs").status_code == 404


def test_redoc_is_not_publicly_exposed() -> None:
    assert _get("/redoc").status_code == 404