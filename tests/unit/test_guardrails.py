from opticargo_agents.guardrails import (
    validate_citations_present_when_required,
    validate_no_transaction_claim,
)


def test_guardrail_blocks_transaction_claim() -> None:
    decision = validate_no_transaction_claim("Booking berhasil dibuat")

    assert decision.allowed is False


def test_guardrail_requires_citation_for_regulation() -> None:
    decision = validate_citations_present_when_required({"intent": "regulation", "citations": []})

    assert decision.allowed is False


def test_guardrail_allows_abstention_without_citation() -> None:
    decision = validate_citations_present_when_required({"intent": "regulation", "abstained": True})

    assert decision.allowed is True
