import pytest

def test_sse_node_trace_schema():
    """Memastikan struktur event trace dari agen AI untuk dikirim via SSE."""
    try:
        from opticargo_agents.contracts import NodeTrace
    except ImportError:
        pytest.skip("NodeTrace tidak ditemukan.")
        
    trace = NodeTrace(node="retrieval", status="running")
    trace_dict = trace.to_dict()
    
    # Field ini penting bagi frontend untuk menganimasikan loading state tiap agen
    assert "node" in trace_dict, "SSE Payload bocor: event trace wajib ada field 'node'"
    assert "status" in trace_dict, "SSE Payload bocor: event trace wajib ada field 'status'"