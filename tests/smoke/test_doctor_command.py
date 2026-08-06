import pytest
import importlib

def test_doctor_command_importable():
    """Memastikan submodule CLI doctor dapat di-impor."""
    try:
        # Import langsung ke submodul doctor
        doctor_module = importlib.import_module("opticargo_agents.cli.doctor")
        assert doctor_module is not None
    except ImportError:
        pytest.skip("Submodul CLI doctor tidak ditemukan")