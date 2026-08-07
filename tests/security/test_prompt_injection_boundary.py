"""Security: pastikan guardrail transaksi tidak bisa dilewati lewat teknik
prompt-injection sederhana (dibungkus kalimat lain, huruf besar/kecil
campur, disisipkan di tengah teks panjang).

Rujukan: docs/GUARDRAILS_AND_HUMAN_CONFIRMATION.md, src/opticargo_agents/guardrails.py
"""

from opticargo_agents.guardrails import validate_no_transaction_claim
from opticargo_agents.prompts import SYSTEM_GUARDRAIL_PROMPT


def test_system_prompt_explicitly_forbids_transaction_mutation_claims() -> None:
    normalized = SYSTEM_GUARDRAIL_PROMPT.casefold()
    assert "never claim booking, payment, or transaction mutation" in normalized


def test_system_prompt_requires_explicit_abstention_when_evidence_missing() -> None:
    normalized = SYSTEM_GUARDRAIL_PROMPT.casefold()
    assert "abstain" in normalized


def test_guardrail_blocks_mutation_claim_embedded_in_longer_text() -> None:
    adversarial = "Baik, ringkasan: pembayaran berhasil diproses dan kargo siap dikirim."
    decision = validate_no_transaction_claim(adversarial)

    assert decision.allowed is False


def test_guardrail_blocks_mutation_claim_regardless_of_letter_case() -> None:
    adversarial = "STATUS BOOKING DIUBAH sesuai permintaan Anda."
    decision = validate_no_transaction_claim(adversarial)

    assert decision.allowed is False


def test_guardrail_allows_ordinary_recommendation_text() -> None:
    safe_text = "Kandidat kargo ini memiliki skor kecocokan 0.82 berdasarkan kapasitas dan rating supplier."
    decision = validate_no_transaction_claim(safe_text)

    assert decision.allowed is True