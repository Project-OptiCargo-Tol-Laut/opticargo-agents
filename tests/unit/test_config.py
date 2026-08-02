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
