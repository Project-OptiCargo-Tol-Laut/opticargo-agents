def test_cli_module_is_importable():
    """Memastikan command-line interface (CLI) dapat diimpor dengan aman."""
    try:
        import opticargo_agents.cli
        assert True
    except ImportError as e:
        assert False, f"Gagal mengimpor opticargo_agents.cli: {e}"