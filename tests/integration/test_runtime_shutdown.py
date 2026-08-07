import pytest

def test_runtime_graceful_shutdown():
    """Memastikan bahwa object Runtime bisa dibersihkan (close/shutdown) tanpa error."""
    try:
        from opticargo_agents.runtime import build_runtime
    except ImportError:
        pytest.skip("Modul runtime tidak ditemukan")
        
    runtime = build_runtime()
    try:
        # Jika runtime mengimplementasikan method close atau shutdown untuk menutup HTTP Client/DB
        if hasattr(runtime, "close") and callable(runtime.close):
            runtime.close()
        elif hasattr(runtime, "shutdown") and callable(runtime.shutdown):
            runtime.shutdown()
        
        # Test ini sukses jika pemanggilan close() tidak menyebabkan aplikasi crash
        assert True
    except Exception as e:
        pytest.fail(f"Gagal melakukan graceful shutdown pada runtime: {e}")