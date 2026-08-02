from opticargo_agents.clients import MLModelsClient
from opticargo_agents.config import load_settings


class FakeTransport:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def post_json(self, url, payload, headers, timeout):
        self.calls.append((url, payload, headers, timeout))
        return self.response


def test_ml_models_client_scores_with_internal_headers() -> None:
    transport = FakeTransport(
        {
            "score": 0.72,
            "model_mode": "heuristic",
            "model_version": "test",
            "fallback_used": True,
            "hard_constraint_valid": True,
            "feature_explanations": [],
            "warnings": [],
        }
    )
    settings = load_settings(
        {
            "ML_MODELS_INTERNAL_URL": "http://ml-models:8000",
            "INTERNAL_SERVICE_TOKEN": "token",
        }
    )
    client = MLModelsClient(settings, transport=transport)

    result = client.score_cargo_match({"voyage": {}, "candidate": {}}, correlation_id="cid-1")

    assert result.score == 0.72
    assert transport.calls[0][2]["X-Internal-Service-Token"] == "token"
    assert transport.calls[0][2]["X-Correlation-ID"] == "cid-1"


def test_ml_models_client_falls_back_when_url_missing() -> None:
    client = MLModelsClient(load_settings({}), transport=FakeTransport({}))

    result = client.score_cargo_match({})

    assert result.available is False
    assert result.fallback_used is True
    assert result.error is not None
    assert result.error.dependency == "ml_models"
