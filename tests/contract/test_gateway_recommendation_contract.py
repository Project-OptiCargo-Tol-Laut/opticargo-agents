import pytest
from dataclasses import fields
from opticargo_agents.contracts import AgentRequest, MLScoreResult

def test_recommendation_request_schema():
    """Memastikan request pencarian voyage valid sesuai kontrak."""
    req_fields = {f.name for f in fields(AgentRequest)}
    
    # Pencarian kargo butuh titik asal dan kargo
    assert "origin_port" in req_fields, "Contract bocor: 'origin_port' wajib untuk pencarian"
    assert "commodity" in req_fields, "Contract bocor: 'commodity' wajib untuk pencarian"

def test_recommendation_scoring_schema():
    """Memastikan hasil scoring kargo dari ML Model tidak berubah."""
    res_fields = {f.name for f in fields(MLScoreResult)}
    
    assert "score" in res_fields, "Contract bocor: ML model harus mengembalikan 'score'"
    assert "hard_constraint_valid" in res_fields, "Contract bocor: filter 'hard_constraint_valid' harus ada"