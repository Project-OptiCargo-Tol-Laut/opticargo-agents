from opticargo_agents.contracts import GraphContextResult, MLScoreResult, RetrievalResult
from opticargo_agents.errors import DependencyUnavailableError
from opticargo_agents.nodes.synthesis import run_synthesis_node


def test_synthesis_node_abstains_when_no_evidence_provided() -> None:
    result = run_synthesis_node(retrieval=None, graph_context=None, ml_score=None)

    assert result.answer_available is False
    assert result.abstained is True


def test_synthesis_node_answers_with_retrieval_citations_only() -> None:
    retrieval = RetrievalResult(
        query="syarat kopra",
        chunks=[{"text": "evidence"}],
        citations=[{"title": "Permendag X"}],
        confidence=0.8,
        abstained=False,
    )

    result = run_synthesis_node(retrieval=retrieval, graph_context=None, ml_score=None)

    assert result.answer_available is True
    assert result.abstained is False
    assert result.citations == [{"title": "Permendag X"}]
    assert result.requires_human_confirmation is False


def test_synthesis_node_abstains_when_retrieval_abstained() -> None:
    retrieval = RetrievalResult(query="syarat kopra", abstained=True, abstention_reason="no citation")

    result = run_synthesis_node(retrieval=retrieval, graph_context=None, ml_score=None)

    assert result.answer_available is False
    assert result.abstained is True
    assert result.abstention_reason == "no citation"


def test_synthesis_node_abstains_when_graph_context_unavailable() -> None:
    error = DependencyUnavailableError("neo4j down", dependency="knowledge_graph")
    graph_context = GraphContextResult(error=error.envelope(), warnings=["neo4j down"])

    result = run_synthesis_node(retrieval=None, graph_context=graph_context, ml_score=None)

    assert result.answer_available is False
    assert result.abstained is True


def test_synthesis_node_abstains_when_ml_score_unavailable() -> None:
    error = DependencyUnavailableError("ml down", dependency="ml_models")
    ml_score = MLScoreResult(error=error.envelope(), fallback_used=True, warnings=["ml down"])

    result = run_synthesis_node(retrieval=None, graph_context=None, ml_score=ml_score)

    assert result.answer_available is False
    assert result.abstained is True


def test_synthesis_node_requires_human_confirmation_when_recommendation_present() -> None:
    ml_score = MLScoreResult(score=0.9, hard_constraint_valid=True)
    graph_context = GraphContextResult(context={"candidates": [{"supplier_id": "s1"}]})

    result = run_synthesis_node(retrieval=None, graph_context=graph_context, ml_score=ml_score)

    assert result.answer_available is True
    assert result.requires_human_confirmation is True


def test_synthesis_node_never_fabricates_citations_from_graph_or_ml() -> None:
    ml_score = MLScoreResult(score=0.9, hard_constraint_valid=True)
    graph_context = GraphContextResult(context={"candidates": [{"supplier_id": "s1"}]})

    result = run_synthesis_node(retrieval=None, graph_context=graph_context, ml_score=ml_score)

    assert result.citations == []