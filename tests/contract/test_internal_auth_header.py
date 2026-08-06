import opticargo_agents.security as security_module

def test_internal_auth_header_contract():
    """Memastikan mekanisme validasi internal token (header auth) tersedia."""
    assert hasattr(security_module, "validate_internal_token"), \
        "Contract bocor: Fungsi 'validate_internal_token' harus ada di security.py untuk autentikasi Gateway"