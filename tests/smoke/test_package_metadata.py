def test_package_has_version():
    """Memastikan package memiliki metadata __version__ yang terbaca."""
    try:
        import opticargo_agents
    except ImportError:
        import pytest
        pytest.fail("Tidak bisa mengimpor base package")

    assert hasattr(opticargo_agents, "__version__"), "Package harus memiliki atribut __version__"
    assert isinstance(opticargo_agents.__version__, str)
    assert len(opticargo_agents.__version__) > 0, "Versi tidak boleh string kosong"