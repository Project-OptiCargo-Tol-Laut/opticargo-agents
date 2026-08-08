"""Evaluasi: pastikan run_synthesis_node ASLI tidak pernah mengarang citation
dari data graph/ML -- citation jawaban akhir hanya boleh berasal dari hasil
retrieval yang sesungguhnya."""

from opticargo_agents.contracts import GraphContextResult, MLScoreResult, RetrievalResult
from opticargo_agents.nodes.synthesis import run_synthesis_node

DATASET_VERSION = "1.0.0"
THRESHOLD = 1.0

DATASET = [
    {
        "name": "retrieval_dengan_citation",
        "retrieval": RetrievalResult(
            query="aturan kopra", citations=[{"title": "Permendag X"}], confidence=0.8, abstained=False
        ),
        "graph_context": None,
        "ml_score": None,
        "expect_citations_nonempty": True,
    },
    {
        "name": "hanya_graph_dan_ml_tanpa_retrieval",
        "retrieval": None,
        "graph_context": GraphContextResult(context={"candidates": [{"supplier_id": "s1"}]}),
        "ml_score": MLScoreResult(score=0.9, hard_constraint_valid=True),
        "expect_citations_nonempty": False,  # tidak boleh mengarang citation dari graph/ML
    },
]


def test_no_fabricated_source() -> None:
    failures = []
    successes = 0

    for case in DATASET:
        result = run_synthesis_node(
            retrieval=case["retrieval"],
            graph_context=case["graph_context"],
            ml_score=case["ml_score"],
        )
        has_citations = len(result.citations) > 0
        if has_citations != case["expect_citations_nonempty"]:
            failures.append({"case": case["name"], "citations": result.citations})
        else:
            successes += 1

    accuracy = successes / len(DATASET)

    assert accuracy >= THRESHOLD, (
        f"No-fabricated-source quality {accuracy*100:.1f}% di bawah ambang {THRESHOLD*100:.1f}%. "
        f"Dataset Version: {DATASET_VERSION}. Failures: {failures}"
    )