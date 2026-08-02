from opticargo_agents.contracts import RetrievalResult, payload_to_dict
from opticargo_agents.errors import DependencyUnavailableError


class Dumpable:
    def model_dump(self, mode: str = "json"):
        return {"mode": mode}


def test_payload_to_dict_supports_pydantic_like_objects() -> None:
    assert payload_to_dict(Dumpable()) == {"mode": "json"}


def test_retrieval_result_serializes_error_envelope() -> None:
    error = DependencyUnavailableError("missing", dependency="rag")
    result = RetrievalResult(query="aturan tol laut", abstained=True, error=error.envelope())

    payload = result.to_dict()

    assert payload["error"]["dependency"] == "rag"
    assert payload["error"]["retryable"] is True
