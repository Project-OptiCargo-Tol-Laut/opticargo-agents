from __future__ import annotations

from dataclasses import dataclass
from typing import Any


MUTATION_KEYWORDS = {
    "booking berhasil",
    "pembayaran berhasil",
    "payment succeeded",
    "status booking diubah",
    "transaksi selesai",
}


@dataclass(frozen=True)
class GuardrailDecision:
    allowed: bool
    reason: str | None = None


def validate_no_transaction_claim(text: str) -> GuardrailDecision:
    normalized = text.casefold()
    for keyword in MUTATION_KEYWORDS:
        if keyword in normalized:
            return GuardrailDecision(False, "Agents must not claim transaction mutation.")
    return GuardrailDecision(True)


def validate_citations_present_when_required(payload: dict[str, Any]) -> GuardrailDecision:
    if payload.get("abstained"):
        return GuardrailDecision(True)
    if payload.get("intent") == "regulation" and not payload.get("citations"):
        return GuardrailDecision(False, "Regulation response requires citation or abstention.")
    return GuardrailDecision(True)


__all__ = [
    "GuardrailDecision",
    "validate_citations_present_when_required",
    "validate_no_transaction_claim",
]
