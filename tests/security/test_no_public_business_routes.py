"""Security: Agents adalah service internal-only. Pastikan permukaan route
ASGI-nya persis sesuai daftar resmi (health, routes introspection, dan
`/internal/v1/*`) -- tidak ada route bisnis publik yang tidak sengaja
terekspos (mis. `/api/...`, `/v1/...` tanpa prefix internal).

Rujukan: docs/SECURITY_BOUNDARY.md, docs/ARCHITECTURE_TARGET.md
"""

import anyio
import httpx

from opticargo_agents.api import app, app_routes


def test_declared_routes_are_all_health_or_internal_prefixed() -> None:
    routes = app_routes()

    for name, path in routes.items():
        is_health_or_introspection = path.startswith("/health/") or path in {"/routes", "/metrics"}
        is_internal = path.startswith("/internal/")
        assert is_health_or_introspection or is_internal, (
            f"Route '{name}' -> '{path}' is neither a health/introspection route "
            "nor prefixed with /internal/; it may be an accidentally public business route."
        )


def test_unprefixed_business_style_path_is_not_routed() -> None:
    async def run_test():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.get("/v1/recommendations")

    response = anyio.run(run_test)
    assert response.status_code == 404


def test_bare_api_path_is_not_routed() -> None:
    async def run_test():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.get("/api/recommendations")

    response = anyio.run(run_test)
    assert response.status_code == 404
