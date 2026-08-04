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


def test_regulation_answer_keeps_citations_on_highest_ranked_document() -> None:
    retrieval = RetrievalResult(
        query="syarat karantina",
        chunks=[{"text": "evidence"}],
        citations=[
            {"document_id": "primary", "title": "UU Karantina", "page": 1},
            {"document_id": "other", "title": "Aturan Angkutan", "page": 2},
            {"document_id": "primary", "title": "UU Karantina", "page": 3},
        ],
        confidence=0.8,
        abstained=False,
    )

    result = run_synthesis_node(retrieval=retrieval)

    assert [citation["title"] for citation in result.citations] == ["UU Karantina", "UU Karantina"]
    assert "Aturan Angkutan" not in result.answer


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


def test_synthesis_node_uses_graph_only_fallback_when_ml_is_unavailable() -> None:
    error = DependencyUnavailableError("ml down", dependency="ml_models")
    ml_score = MLScoreResult(error=error.envelope(), fallback_used=True, warnings=["ml down"])
    graph_context = GraphContextResult(
        context={
            "candidates": [
                {
                    "supplier": {"supplier_name": "PT Kopra Timur"},
                    "commodity_name": "Kopra",
                    "available_weight_ton": 20,
                }
            ]
        }
    )

    result = run_synthesis_node(retrieval=None, graph_context=graph_context, ml_score=ml_score)

    assert result.answer_available is True
    assert result.abstained is False
    assert "Knowledge Graph saja" in result.answer
    assert result.requires_human_confirmation is True


def test_route_answer_does_not_attach_unrelated_regulation_citations() -> None:
    retrieval = RetrievalResult(
        query="jelaskan rute",
        chunks=[{"text": "evidence"}],
        citations=[{"title": "Peraturan yang tidak diminta"}],
        confidence=0.8,
        abstained=False,
    )
    graph_context = GraphContextResult(context={"active_leg": {}, "candidates": []})

    result = run_synthesis_node(retrieval=retrieval, graph_context=graph_context, ml_score=None)

    assert result.answer_available is True
    assert result.citations == []


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
