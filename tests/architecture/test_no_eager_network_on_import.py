import importlib
import sys
import pytest
from unittest.mock import patch
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

@pytest.fixture
def mock_network():
    """Mock socket module to catch eager connections."""
    with patch("socket.socket") as mock_sock:
        mock_sock.side_effect = RuntimeError("Network call terdeteksi saat fase import!")
        yield mock_sock

def test_package_imports_without_network_calls(mock_network):
    """Memastikan tidak ada koneksi jaringan (eager initialization) saat import root package."""
    # Pastikan module belum ter-load sebelumnya
    if "opticargo_agents" in sys.modules:
        del sys.modules["opticargo_agents"]
        
    try:
        importlib.import_module("opticargo_agents")
    except RuntimeError as e:
        pytest.fail(f"Arsitektur Bocor: {str(e)}")