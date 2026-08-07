"""Security: pastikan URL dependency (Neo4j, Qdrant, ML Models) yang dibaca
dari environment divalidasi skemanya sebelum dipakai untuk membangun
koneksi/HTTP request -- mencegah URL berskema berbahaya (mis. `file://`,
`gopher://`) atau typo skema lolos sampai ke `urlopen`/driver call.

Rujukan: src/opticargo_agents/README.md ("memvalidasi URL/scheme/range")
"""

from opticargo_agents.config import (
    HTTP_DEPENDENCY_URL_ALLOWED_SCHEMES,
    NEO4J_URI_ALLOWED_SCHEMES,
    load_settings,
    validate_dependency_url,
)


def test_empty_url_is_treated_as_not_configured_and_allowed() -> None:
    validate_dependency_url("ML_MODELS_INTERNAL_URL", "", HTTP_DEPENDENCY_URL_ALLOWED_SCHEMES)  # no raise


def test_http_and_https_are_allowed_for_http_dependencies() -> None:
    validate_dependency_url("QDRANT_URL", "http://qdrant:6333", HTTP_DEPENDENCY_URL_ALLOWED_SCHEMES)
    validate_dependency_url("QDRANT_URL", "https://qdrant.internal:6333", HTTP_DEPENDENCY_URL_ALLOWED_SCHEMES)


def test_bolt_and_neo4j_schemes_are_allowed_for_neo4j() -> None:
    validate_dependency_url("NEO4J_URI", "bolt://neo4j:7687", NEO4J_URI_ALLOWED_SCHEMES)
    validate_dependency_url("NEO4J_URI", "neo4j+s://neo4j.internal:7687", NEO4J_URI_ALLOWED_SCHEMES)


def test_dangerous_file_scheme_is_rejected_for_http_dependency() -> None:
    try:
        validate_dependency_url("QDRANT_URL", "file:///etc/passwd", HTTP_DEPENDENCY_URL_ALLOWED_SCHEMES)
        assert False, "Expected ValueError for file:// scheme"
    except ValueError:
        pass


def test_http_scheme_is_rejected_for_neo4j_uri() -> None:
    try:
        validate_dependency_url("NEO4J_URI", "http://neo4j:7687", NEO4J_URI_ALLOWED_SCHEMES)
        assert False, "Expected ValueError: Neo4j driver URIs must use bolt/neo4j schemes, not http"
    except ValueError:
        pass


def test_load_settings_rejects_misconfigured_dependency_url_at_startup() -> None:
    try:
        load_settings({"QDRANT_URL": "file:///etc/passwd"})
        assert False, "Expected ValueError to fail fast on a dangerous QDRANT_URL scheme"
    except ValueError:
        pass


def test_load_settings_accepts_default_configuration() -> None:
    settings = load_settings({})  # must not raise: defaults are safe
    assert settings.neo4j_uri.startswith("bolt://")
    assert settings.qdrant_url.startswith("http://")