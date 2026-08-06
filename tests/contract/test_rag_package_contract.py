import pytest
from dataclasses import fields
from opticargo_agents.contracts import RetrievalResult, RetrievalRequest

def test_rag_request_schema():
    """Memastikan parameter pencarian dokumen sesuai."""
    req_fields = {f.name for f in fields(RetrievalRequest)}
    assert "query" in req_fields, "Pencarian RAG butuh 'query'"
    assert "min_score" in req_fields, "Pencarian RAG harus memiliki filter 'min_score'"

def test_rag_result_schema():
    """Memastikan hasil pencarian dokumen (RAG) memenuhi standar."""
    res_fields = {f.name for f in fields(RetrievalResult)}
    assert "chunks" in res_fields, "RAG harus mengembalikan potongan teks ('chunks')"
    assert "citations" in res_fields, "RAG harus mengembalikan sitasi dokumen ('citations')"
    assert "abstained" in res_fields, "RAG harus tau kapan menyerah (abstain)"