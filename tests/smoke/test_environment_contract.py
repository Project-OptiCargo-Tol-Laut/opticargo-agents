import pytest

def test_settings_can_load_from_empty_env():
    """Memastikan sistem tidak crash jika environment variables kosong."""
    try:
        from opticargo_agents.config import load_settings
    except ImportError:
        pytest.skip("Modul config.py tidak ditemukan")

    try:
        # Memaksa muat dengan kamus/env kosong
        settings = load_settings({})
        assert settings is not None
        assert hasattr(settings, "environment")
    except Exception as e:
        pytest.fail(f"Gagal memuat setting (kemungkinan ada env var wajib tanpa fallback): {e}")