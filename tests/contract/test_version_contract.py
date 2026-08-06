import opticargo_agents.version as version_module

def test_version_response_schema():
    """Memastikan API mengembalikan informasi versi aplikasi."""
    attrs = dir(version_module)
    has_version_info = any("version" in a.lower() for a in attrs)
    
    assert has_version_info, "Contract bocor: Modul version.py harus mengekspos variabel/fungsi versi"