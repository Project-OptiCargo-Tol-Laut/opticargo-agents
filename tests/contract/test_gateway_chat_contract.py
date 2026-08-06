import pytest
from dataclasses import fields
from opticargo_agents.contracts import AgentRequest, SynthesisResult

def test_agent_request_schema():
    """Memastikan AgentRequest (input dari Gateway) memiliki field yang benar."""
    req_fields = {f.name for f in fields(AgentRequest)}
    
    assert "query" in req_fields, "Contract bocor: 'query' wajib ada"
    assert "correlation_id" in req_fields, "Contract bocor: 'correlation_id' wajib ada"
    assert "requested_intent" in req_fields, "Contract bocor: 'requested_intent' wajib ada"
    assert "voyage_id" in req_fields, "Contract bocor: 'voyage_id' wajib ada"

def test_synthesis_result_schema():
    """Memastikan SynthesisResult (output AI) memenuhi kontrak."""
    res_fields = {f.name for f in fields(SynthesisResult)}
    
    assert "answer" in res_fields, "Contract bocor: 'answer' wajib ada"
    assert "citations" in res_fields, "Contract bocor: 'citations' wajib ada"
    assert "requires_human_confirmation" in res_fields, "Contract bocor: harus mendukung status konfirmasi"