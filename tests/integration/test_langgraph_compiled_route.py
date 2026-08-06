import pytest
from opticargo_agents.orchestrator.graph import WorkflowRunner, WORKFLOW_ROUTES, WorkflowNodes

def test_workflow_runner_routes_exist():
    """Memastikan kamus WORKFLOW_ROUTES memiliki jalur intent yang lengkap dan valid."""
    expected_intents = ["regulation", "matching", "route", "analytics", "unknown"]
    
    for intent in expected_intents:
        assert intent in WORKFLOW_ROUTES, f"Route untuk intent '{intent}' wajib didefinisikan"
        route_steps = WORKFLOW_ROUTES[intent]
        assert isinstance(route_steps, list), f"Langkah rute untuk '{intent}' harus berupa list"
        assert len(route_steps) > 0, f"Rute '{intent}' tidak boleh kosong"

def test_workflow_runner_initialization():
    """Memastikan WorkflowRunner dapat diinisialisasi dengan baik."""
    try:
        runner = WorkflowRunner()
        assert runner is not None
        assert isinstance(runner.nodes, WorkflowNodes)
    except Exception as e:
        pytest.fail(f"WorkflowRunner gagal diinisialisasi: {e}")

def test_workflow_runner_route_resolution():
    """Memastikan method route_for mengembalikan urutan node yang benar sesuai intent."""
    runner = WorkflowRunner()
    
    # Uji intent matching
    matching_route = runner.route_for("matching")
    assert "intent" in matching_route
    assert "graph" in matching_route
    assert "optimization" in matching_route
    
    # Uji intent unknown (fallback)
    unknown_route = runner.route_for("unknown")
    assert "intent" in unknown_route
    assert "synthesis" in unknown_route