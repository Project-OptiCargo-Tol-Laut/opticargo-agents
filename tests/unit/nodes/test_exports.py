from opticargo_agents.nodes import (
    run_cargo_scoring_node,
    run_graph_analysis_node,
    run_intent_node,
    run_retrieval_node,
    run_synthesis_node,
)


def test_nodes_export_workflow_callables() -> None:
    assert callable(run_intent_node)
    assert callable(run_graph_analysis_node)
    assert callable(run_cargo_scoring_node)
    assert callable(run_retrieval_node)
    assert callable(run_synthesis_node)
