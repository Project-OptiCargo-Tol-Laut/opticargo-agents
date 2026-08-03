from opticargo_agents.clients.llm import LLMClient


def test_llm_client_uses_deterministic_fallback() -> None:
    result = LLMClient().complete("hello")

    assert result.fallback_used is True
    assert result.warning == "LLM is not configured."
