import importlib
import pytest

def test_core_packages_are_importable():
    """Memastikan modul utama bisa diimpor tanpa error syntax/dependencies."""
    packages = [
        "opticargo_agents",
        "opticargo_agents.cli",
        "opticargo_agents.clients",
        "opticargo_agents.integrations",
        "opticargo_agents.nodes",
        "opticargo_agents.orchestrator"
    ]
    
    for pkg in packages:
        try:
            importlib.import_module(pkg)
        except ImportError as e:
            pytest.fail(f"Smoke test gagal: Tidak bisa mengimpor {pkg}. Error: {e}")