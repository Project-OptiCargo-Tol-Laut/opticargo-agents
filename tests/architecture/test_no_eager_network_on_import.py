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
    # Simpan module opticargo_agents.* yang sudah ter-cache, supaya bisa dikembalikan
    # setelah test selesai -- tanpa ini, test lain yang jalan setelahnya bisa
    # mendapati sys.modules dalam kondisi tidak konsisten (submodule tidak
    # ter-attach ulang ke parent package yang baru).
    saved_modules = {
        name: module
        for name, module in sys.modules.items()
        if name == "opticargo_agents" or name.startswith("opticargo_agents.")
    }
    for name in saved_modules:
        del sys.modules[name]

    try:
        importlib.import_module("opticargo_agents")
    except RuntimeError as e:
        pytest.fail(f"Arsitektur Bocor: {str(e)}")
    finally:
        for name in list(sys.modules):
            if name == "opticargo_agents" or name.startswith("opticargo_agents."):
                del sys.modules[name]
        sys.modules.update(saved_modules)