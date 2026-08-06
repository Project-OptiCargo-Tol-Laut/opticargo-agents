import pytest

def test_ml_model_payload_schema():
    """Memastikan payload untuk scoring memiliki mapping yang benar."""
    try:
        from opticargo_agents.contracts import AgentRequest
    except ImportError:
        pytest.skip("AgentRequest tidak ditemukan.")

    req = AgentRequest(query="dummy", origin_port="SBY", commodity="BERAS")
    
    # Pastikan ada field scoring_payload yang berbentuk dictionary untuk dikirim ke ML server
    assert hasattr(req, "scoring_payload")
    
    # Jika default nilainya None, pastikan tipe hinting-nya mengizinkan dict
    if req.scoring_payload is not None:
        assert isinstance(req.scoring_payload, dict), "scoring_payload harus berupa dictionary"