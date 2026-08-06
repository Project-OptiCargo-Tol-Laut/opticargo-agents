def test_clients_module_is_importable():
    """Memastikan package clients tidak memiliki circular dependency."""
    try:
        import opticargo_agents.clients
        assert True
    except ImportError as e:
        assert False, f"Gagal mengimpor opticargo_agents.clients: {e}"