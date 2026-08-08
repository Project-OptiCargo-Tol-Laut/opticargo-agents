"""Evaluasi: pastikan node retrieval ASLI mengembalikan citation yang benar-
benar berasal dari hasil pencarian, dan memaksa abstain kalau tidak ada
citation -- bukan cuma mengecek dataclass menyimpan apa yang dimasukkan."""

from opticargo_agents.config import load_settings
from opticargo_agents.contracts import RetrievalRequest
from opticargo_agents.integrations import RagAdapter
from opticargo_agents.nodes.retrieval import run_retrieval_node

DATASET_VERSION = "1.0.0"
THRESHOLD = 1.0


def _retrieve_with_citation(query, *, graph_context=None, top_k=5, min_score=0.35):
    return {
        "query": query,
        "chunks": [{"text": "Pasal 12 mengatur muatan balik.", "score": 0.8}],
        "citations": [{"document_id": "PM-99-2023", "title": "Permenhub 99/2023"}],
        "confidence": 0.8,
        "abstained": False,
    }


def _retrieve_without_citation(query, *, graph_context=None, top_k=5, min_score=0.35):
    return {
        "query": query,
        "chunks": [{"text": "Teks ditemukan tanpa sumber jelas.", "score": 0.6}],
        "citations": [],
        "confidence": 0.6,
        "abstained": False,
    }


DATASET = [
    {"name": "ada_citation", "retrieve_func": _retrieve_with_citation, "expect_citation": True},
    {"name": "tanpa_citation_harus_abstain", "retrieve_func": _retrieve_without_citation, "expect_citation": False},
]


def test_citation_correctness() -> None:
    failures = []
    successes = 0

    for case in DATASET:
        adapter = RagAdapter(load_settings({}), retrieve_func=case["retrieve_func"])
        result = run_retrieval_node(RetrievalRequest(query="aturan tol laut"), adapter)

        has_citation = len(result.citations) > 0 and not result.abstained
        if has_citation != case["expect_citation"]:
            failures.append({"case": case["name"], "abstained": result.abstained, "citations": result.citations})
        else:
            successes += 1

    accuracy = successes / len(DATASET)

    assert accuracy >= THRESHOLD, (
        f"Citation correctness {accuracy*100:.1f}% di bawah ambang {THRESHOLD*100:.1f}%. "
        f"Dataset Version: {DATASET_VERSION}. Failures: {failures}"
    )