from opticargo_agents.protocols import GraphProvider, RetrievalProvider, ScoringProvider


def test_protocols_are_importable() -> None:
    assert GraphProvider
    assert RetrievalProvider
    assert ScoringProvider
