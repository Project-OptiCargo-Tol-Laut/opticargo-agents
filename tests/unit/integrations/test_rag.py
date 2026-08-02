from opticargo_agents.config import load_settings
from opticargo_agents.contracts import RetrievalRequest
from opticargo_agents.integrations import RagAdapter


def test_rag_adapter_normalizes_retrieval_result() -> None:
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

    result = adapter.retrieve(RetrievalRequest(query="aturan tol laut", top_k=3))

    assert result.abstained is False
    assert result.confidence == 0.8
    assert len(result.citations) == 1


def test_rag_adapter_abstains_when_dependency_fails() -> None:
    def retrieve(*args, **kwargs):
        raise RuntimeError("qdrant unavailable")

    adapter = RagAdapter(load_settings({}), retrieve_func=retrieve)

    result = adapter.retrieve(RetrievalRequest(query="aturan"))

    assert result.abstained is True
    assert result.error is not None
    assert result.error.dependency == "rag"
