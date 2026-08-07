"""Security: pastikan perbandingan token internal memakai constant-time
comparison (secrets.compare_digest), bukan operator `==` string biasa yang
rentan timing attack.

Ini test statis terhadap sumber (bukan pengukuran waktu, yang tidak
reliabel di lingkungan CI) plus test fungsional bahwa token dengan panjang
sama tapi isi berbeda tetap ditolak secara konsisten.
"""

import inspect

from opticargo_agents import security
from opticargo_agents.config import load_settings
from opticargo_agents.errors import UnauthorizedInternalRequestError


def test_validate_internal_token_uses_constant_time_compare() -> None:
    source = inspect.getsource(security.validate_internal_token)
    assert "secrets.compare_digest" in source, (
        "Internal token comparison must use secrets.compare_digest to avoid timing attacks, "
        "not a plain '==' string comparison."
    )
    assert "provided_token == expected" not in source
    assert "expected == provided_token" not in source


def test_same_length_wrong_token_is_still_rejected() -> None:
    settings = load_settings({"OPTICARGO_ENVIRONMENT": "production", "INTERNAL_SERVICE_TOKEN": "abcdefgh"})
    try:
        security.validate_internal_token("abcdefgX", settings)  # same length, last char differs
        assert False, "Expected UnauthorizedInternalRequestError"
    except UnauthorizedInternalRequestError:
        pass


def test_different_length_token_is_rejected() -> None:
    settings = load_settings({"OPTICARGO_ENVIRONMENT": "production", "INTERNAL_SERVICE_TOKEN": "abcdefgh"})
    try:
        security.validate_internal_token("short", settings)
        assert False, "Expected UnauthorizedInternalRequestError"
    except UnauthorizedInternalRequestError:
        pass