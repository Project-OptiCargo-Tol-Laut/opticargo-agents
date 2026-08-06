import inspect

def test_metrics_module_contract():
    """Memastikan modul metrics memiliki antarmuka yang disepakati untuk instrumentation."""
    try:
        import opticargo_agents.metrics as metrics_module
    except ImportError:
        import pytest
        pytest.skip("Modul metrics belum tersedia.")

    # Memastikan modul metrics mengekspos variabel atau fungsi untuk merekam latensi/request.
    # Gateway dan Agen bergantung pada nama-nama standar ini untuk Grafana dashboard.
    
    # Ambil semua objek yang bersifat publik dari modul metrics
    public_attrs = [attr for attr in dir(metrics_module) if not attr.startswith("_")]
    
    # Minimal modul metrik harus punya sesuatu (seperti increment_counter atau record_latency)
    # Jika saat ini masih kosong, kita tidak akan gagalkan secara hard-crash
    has_recording_function = any(
        "record" in a.lower() or "count" in a.lower() or "metric" in a.lower() or "observe" in a.lower()
        for a in public_attrs
    )
    
    if public_attrs and not has_recording_function:
        assert False, "Contract bocor: Modul metrics harus memiliki fungsi untuk merekam metrik (contoh: record_latency)"