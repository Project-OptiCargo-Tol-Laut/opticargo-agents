"""Security: Agents adalah service rekomendasi & analitik read-only -- ia
tidak boleh pernah mendefinisikan, menyimpan, atau meneruskan credential
pembayaran/transaksi (nomor kartu, CVV, rekening bank, PIN) di kontrak
typed-nya sama sekali.

Ini melengkapi tests/architecture/test_no_transaction_mutation.py (yang
mengunci larangan method mutation) dengan mengunci larangan field data
credential pada level skema.

Rujukan: docs/SECURITY_BOUNDARY.md
"""

import dataclasses
import inspect

from opticargo_agents import contracts

FORBIDDEN_FIELD_SUBSTRINGS = (
    "card_number",
    "cvv",
    "cvc",
    "pin",
    "bank_account",
    "account_number",
    "routing_number",
    "payment_method",
    "card_expiry",
)


def _all_contract_dataclasses() -> list[type]:
    return [
        obj
        for _, obj in inspect.getmembers(contracts, inspect.isclass)
        if dataclasses.is_dataclass(obj) and obj.__module__ == contracts.__name__
    ]


def test_no_contract_dataclass_defines_a_payment_credential_field() -> None:
    dataclass_types = _all_contract_dataclasses()
    assert dataclass_types, "Expected at least one dataclass in contracts module"

    offenders = []
    for cls in dataclass_types:
        for f in dataclasses.fields(cls):
            field_name = f.name.casefold()
            for forbidden in FORBIDDEN_FIELD_SUBSTRINGS:
                if forbidden in field_name:
                    offenders.append(f"{cls.__name__}.{f.name}")

    assert not offenders, f"Payment credential-like fields found in contracts: {offenders}"


def test_agent_request_carries_no_payment_credential_fields() -> None:
    request_fields = {f.name for f in dataclasses.fields(contracts.AgentRequest)}
    for forbidden in FORBIDDEN_FIELD_SUBSTRINGS:
        assert not any(forbidden in name for name in request_fields), (
            f"AgentRequest must never carry a '{forbidden}'-like field; "
            "Agents does not process payment transactions."
        )