import pytest
from dataclasses import fields
from opticargo_agents.contracts import GraphContextRequest, GraphContextResult

def test_graph_request_schema():
    """Memastikan parameter query Graph valid."""
    req_fields = {f.name for f in fields(GraphContextRequest)}
    # Minimal ada kargo atau id pelayaran untuk di query
    assert "voyage_id" in req_fields
    assert "origin_port" in req_fields

def test_graph_result_schema():
    """Memastikan hasil query Graph memenuhi standar untuk context agen."""
    res_fields = {f.name for f in fields(GraphContextResult)}
    assert "context" in res_fields, "Hasil graph harus membungkus datanya dalam 'context'"