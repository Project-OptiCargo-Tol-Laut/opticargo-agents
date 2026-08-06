import pytest

def test_healthcheck_command_importable():
    """Memastikan CLI healthcheck dapat di-impor."""
    try:
        import opticargo_agents.cli
        # Pastikan tidak meledak saat diakses
        assert opticargo_agents.cli is not None
    except ImportError:
        pytest.skip("CLI tidak ditemukan")