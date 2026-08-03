from opticargo_agents.config import load_settings


def test_load_settings_uses_defaults() -> None:
    settings = load_settings({})

    assert settings.environment == "development"
    assert settings.port == 8000
    assert settings.rag_top_k == 5


def test_load_settings_reads_integration_env() -> None:
    settings = load_settings(
        {
            "AGENTS_PORT": "8080",
            "ML_MODELS_INTERNAL_URL": "http://ml-models:8000",
            "RAG_TOP_K": "7",
            "READINESS_REQUIRE_ML_MODELS": "true",
        }
    )

    assert settings.port == 8080
    assert settings.ml_models_internal_url == "http://ml-models:8000"
    assert settings.rag_top_k == 7
    assert settings.readiness_require_ml_models is True


def test_load_settings_reads_ml_payload_defaults() -> None:
    settings = load_settings(
        {
            "DEFAULT_OPERATING_COST_PER_KM_IDR": "150000",
            "DEFAULT_MARKET_RATE_PER_TON_IDR": "900000",
            "DEFAULT_SUPPLIER_SUCCESS_RATE": "0.9",
        }
    )

    assert settings.default_operating_cost_per_km_idr == 150000
    assert settings.default_market_rate_per_ton_idr == 900000
    assert settings.default_supplier_success_rate == 0.9
