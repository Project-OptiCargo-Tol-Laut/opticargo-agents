import pytest
from uuid import uuid4
from opticargo_agents.contracts import AgentRequest

@pytest.fixture
def mock_agent_request():
    """Fixture dasar untuk mensimulasikan input pengguna dari Gateway."""
    return AgentRequest(
        query="Carikan kargo dari Surabaya ke Makassar",
        correlation_id=uuid4(),
        requested_intent="matching",
        origin_port="Surabaya",
        top_k=5
    )