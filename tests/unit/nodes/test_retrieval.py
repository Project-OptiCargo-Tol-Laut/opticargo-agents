from opticargo_agents.config import load_settings
from opticargo_agents.contracts import RetrievalRequest
from opticargo_agents.integrations import RagAdapter
from opticargo_agents.nodes.retrieval import run_retrieval_node


def test_retrieval_node_passes_through_when_citation_present() -> None:
    def retrieve(query, graph_context=None, top_k=5, min_score=0.35):
        return {
            "query": query,
            "chunks": [{"text": "evidence", "score": 0.8}],
            "citations": [{"title": "Dokumen A"}],
            "confidence": "0.8",
            "abstained": False,
            "warnings": [],
        }

    adapter = RagAdapter(load_settings({}), retrieve_func=retrieve)
    result = run_retrieval_node(RetrievalRequest(query="aturan tol laut"), adapter)

    assert result.abstained is False
    assert len(result.citations) == 1


def test_retrieval_node_forces_abstention_when_citation_missing() -> None:
    def retrieve(query, graph_context=None, top_k=5, min_score=0.35):
        return {
            "query": query,
            "chunks": [{"text": "evidence tanpa sumber jelas", "score": 0.6}],
            "citations": [],
            "confidence": "0.6",
            "abstained": False,
            "warnings": [],
        }

    adapter = RagAdapter(load_settings({}), retrieve_func=retrieve)
    result = run_retrieval_node(RetrievalRequest(query="aturan tol laut"), adapter)

    assert result.abstained is True
    assert result.abstention_reason is not None
    assert "citation" in result.abstention_reason.lower()


def test_retrieval_node_forces_abstention_when_confidence_below_min_score() -> None:
    def retrieve(query, graph_context=None, top_k=5, min_score=0.35):
        return {
            "query": query,
            "chunks": [{"text": "evidence lemah", "score": 0.1}],
            "citations": [{"title": "Dokumen B"}],
            "confidence": "0.1",
            "abstained": False,
            "warnings": [],
        }

    adapter = RagAdapter(load_settings({}), retrieve_func=retrieve)
    result = run_retrieval_node(RetrievalRequest(query="aturan tol laut", min_score=0.35), adapter)

    assert result.abstained is True
    assert result.abstention_reason is not None
    assert "confidence" in result.abstention_reason.lower()


def test_retrieval_node_passes_through_when_confidence_meets_min_score_exactly() -> None:
    def retrieve(query, graph_context=None, top_k=5, min_score=0.35):
        return {
            "query": query,
            "chunks": [{"text": "evidence pas batas", "score": 0.35}],
            "citations": [{"title": "Dokumen C"}],
            "confidence": "0.35",
            "abstained": False,
            "warnings": [],
        }

    adapter = RagAdapter(load_settings({}), retrieve_func=retrieve)
    result = run_retrieval_node(RetrievalRequest(query="aturan tol laut", min_score=0.35), adapter)

    assert result.abstained is False


def test_retrieval_node_preserves_existing_abstention_reason() -> None:
    def retrieve(*args, **kwargs):
        raise RuntimeError("qdrant unavailable")

    adapter = RagAdapter(load_settings({}), retrieve_func=retrieve)
    result = run_retrieval_node(RetrievalRequest(query="aturan"), adapter)

    assert result.abstained is True
    assert result.error is not None
    assert result.error.dependency == "rag"