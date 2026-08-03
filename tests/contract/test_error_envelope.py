from opticargo_agents.errors import DependencyUnavailableError


def test_error_envelope_shape_is_stable() -> None:
    payload = DependencyUnavailableError("down", dependency="rag").envelope().to_dict()

    assert set(payload) == {"code", "message", "dependency", "retryable"}
    assert payload["code"] == "dependency_unavailable"
    assert payload["dependency"] == "rag"
    assert payload["retryable"] is True
