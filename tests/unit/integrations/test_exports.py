def test_integrations_module_is_importable():
    """Memastikan package integrations dapat diakses tanpa error."""
    try:
        import opticargo_agents.integrations
        assert True
    except ImportError as e:
        assert False, f"Gagal mengimpor opticargo_agents.integrations: {e}"