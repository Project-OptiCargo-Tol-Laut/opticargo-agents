from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Mapping
from urllib.parse import urlparse

NEO4J_URI_ALLOWED_SCHEMES = frozenset({"bolt", "bolt+s", "bolt+ssc", "neo4j", "neo4j+s", "neo4j+ssc"})
HTTP_DEPENDENCY_URL_ALLOWED_SCHEMES = frozenset({"http", "https"})


def validate_dependency_url(name: str, url: str, allowed_schemes: frozenset[str]) -> None:
    """Fail fast on a dependency URL whose scheme is not explicitly allowed.

    An empty string means "not configured" and is always accepted -- callers
    (health checks, clients) already treat that as a degraded/optional
    dependency. Anything else must use one of the allowed schemes, so a
    misconfigured or malicious URL (e.g. `file://`, `gopher://`) can never
    reach `urlopen`/driver calls built from internal config.
    """
    if not url:
        return
    scheme = urlparse(url).scheme.lower()
    if scheme not in allowed_schemes:
        raise ValueError(
            f"{name} has an unsupported URL scheme '{scheme or '(none)'}'. "
            f"Allowed schemes: {sorted(allowed_schemes)}."
        )


def _str(env: Mapping[str, str], name: str, default: str = "") -> str:
    value = env.get(name)
    return default if value is None or value == "" else value


def _int(env: Mapping[str, str], name: str, default: int) -> int:
    try:
        return int(_str(env, name, str(default)))
    except ValueError:
        return default


def _float(env: Mapping[str, str], name: str, default: float) -> float:
    try:
        return float(_str(env, name, str(default)))
    except ValueError:
        return default


def _bool(env: Mapping[str, str], name: str, default: bool) -> bool:
    raw = _str(env, name, str(default)).strip().lower()
    return raw in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    environment: str = "development"
    release: str = "local"
    git_sha: str = "unknown"
    shared_version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8000
    request_timeout_seconds: float = 10.0
    max_concurrent_requests: int = 16
    max_top_n: int = 10
    enable_openapi: bool = True
    internal_service_token: str = ""
    correlation_header: str = "X-Correlation-ID"
    ml_models_internal_url: str = ""
    ml_model_request_timeout_seconds: float = 5.0
    ml_model_max_retries: int = 1
    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""
    neo4j_database: str = "neo4j"
    graph_query_timeout_seconds: float = 5.0
    graph_search_radius_km: float = 150.0
    graph_tolerance_days: int = 3
    qdrant_url: str = "http://qdrant:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "opticargo_documents_v1"
    rag_top_k: int = 5
    rag_min_score: float = 0.35
    readiness_require_ml_models: bool = False
    readiness_require_neo4j: bool = False
    readiness_require_qdrant: bool = False
    readiness_require_llm: bool = False
    default_operating_cost_per_km_idr: float = 125000.0
    default_market_rate_per_ton_idr: float = 750000.0
    default_asking_price_per_ton_idr: float = 700000.0
    default_cargo_volume_m3_per_ton: float = 1.0
    default_supplier_rating: float = 4.0
    default_supplier_success_rate: float = 0.85
    default_supplier_cancellation_rate: float = 0.05
    log_level: str = "INFO"
    log_format: str = "json"


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    source = os.environ if env is None else env
    neo4j_uri = _str(source, "NEO4J_URI", "bolt://neo4j:7687")
    qdrant_url = _str(source, "QDRANT_URL", "http://qdrant:6333")
    ml_models_internal_url = _str(source, "ML_MODELS_INTERNAL_URL", "")
    validate_dependency_url("NEO4J_URI", neo4j_uri, NEO4J_URI_ALLOWED_SCHEMES)
    validate_dependency_url("QDRANT_URL", qdrant_url, HTTP_DEPENDENCY_URL_ALLOWED_SCHEMES)
    validate_dependency_url(
        "ML_MODELS_INTERNAL_URL", ml_models_internal_url, HTTP_DEPENDENCY_URL_ALLOWED_SCHEMES
    )
    return Settings(
        environment=_str(source, "OPTICARGO_ENVIRONMENT", "development"),
        release=_str(source, "OPTICARGO_RELEASE", "local"),
        git_sha=_str(source, "OPTICARGO_GIT_SHA", "unknown"),
        shared_version=_str(source, "OPTICARGO_SHARED_VERSION", "1.0.0"),
        host=_str(source, "AGENTS_HOST", "0.0.0.0"),
        port=_int(source, "AGENTS_PORT", 8000),
        request_timeout_seconds=_float(source, "AGENTS_REQUEST_TIMEOUT_SECONDS", 10.0),
        max_concurrent_requests=_int(source, "AGENTS_MAX_CONCURRENT_REQUESTS", 16),
        max_top_n=_int(source, "AGENTS_MAX_TOP_N", 10),
        enable_openapi=_bool(source, "AGENTS_ENABLE_OPENAPI", True),
        internal_service_token=_str(source, "INTERNAL_SERVICE_TOKEN", ""),
        correlation_header=_str(source, "CORRELATION_HEADER", "X-Correlation-ID"),
        ml_models_internal_url=ml_models_internal_url,
        ml_model_request_timeout_seconds=_float(source, "ML_MODEL_REQUEST_TIMEOUT_SECONDS", 5.0),
        ml_model_max_retries=_int(source, "ML_MODEL_MAX_RETRIES", 1),
        neo4j_uri=neo4j_uri,
        neo4j_user=_str(source, "NEO4J_USER", "neo4j"),
        neo4j_password=_str(source, "NEO4J_PASSWORD", ""),
        neo4j_database=_str(source, "NEO4J_DATABASE", "neo4j"),
        graph_query_timeout_seconds=_float(source, "GRAPH_QUERY_TIMEOUT_SECONDS", 5.0),
        graph_search_radius_km=_float(source, "GRAPH_SEARCH_RADIUS_KM", 150.0),
        graph_tolerance_days=_int(source, "GRAPH_TOLERANCE_DAYS", 3),
        qdrant_url=qdrant_url,
        qdrant_api_key=_str(source, "QDRANT_API_KEY", ""),
        qdrant_collection=_str(source, "QDRANT_COLLECTION", "opticargo_documents_v1"),
        rag_top_k=_int(source, "RAG_TOP_K", 5),
        rag_min_score=_float(source, "RAG_MIN_SCORE", 0.35),
        readiness_require_ml_models=_bool(source, "READINESS_REQUIRE_ML_MODELS", False),
        readiness_require_neo4j=_bool(source, "READINESS_REQUIRE_NEO4J", False),
        readiness_require_qdrant=_bool(source, "READINESS_REQUIRE_QDRANT", False),
        readiness_require_llm=_bool(source, "READINESS_REQUIRE_LLM", False),
        default_operating_cost_per_km_idr=_float(
            source, "DEFAULT_OPERATING_COST_PER_KM_IDR", 125000.0
        ),
        default_market_rate_per_ton_idr=_float(source, "DEFAULT_MARKET_RATE_PER_TON_IDR", 750000.0),
        default_asking_price_per_ton_idr=_float(source, "DEFAULT_ASKING_PRICE_PER_TON_IDR", 700000.0),
        default_cargo_volume_m3_per_ton=_float(source, "DEFAULT_CARGO_VOLUME_M3_PER_TON", 1.0),
        default_supplier_rating=_float(source, "DEFAULT_SUPPLIER_RATING", 4.0),
        default_supplier_success_rate=_float(source, "DEFAULT_SUPPLIER_SUCCESS_RATE", 0.85),
        default_supplier_cancellation_rate=_float(source, "DEFAULT_SUPPLIER_CANCELLATION_RATE", 0.05),
        log_level=_str(source, "LOG_LEVEL", "INFO"),
        log_format=_str(source, "LOG_FORMAT", "json"),
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return load_settings()