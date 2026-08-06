from opticargo_agents.errors import ErrorEnvelope

def test_error_envelope_creation():
    """Memastikan ErrorEnvelope menyimpan dan mengubah data ke dict dengan benar."""
    error = ErrorEnvelope(
        code="TEST_ERR_001", 
        message="Ini adalah error simulasi", 
        dependency="neo4j",
        retryable=True
    )
    
    # Assert properti objek
    assert error.code == "TEST_ERR_001"
    assert error.message == "Ini adalah error simulasi"
    assert error.dependency == "neo4j"
    assert error.retryable is True
    
    # Assert hasil konversi dictionary
    err_dict = error.to_dict()
    assert err_dict["code"] == "TEST_ERR_001"
    assert err_dict["message"] == "Ini adalah error simulasi"
    assert err_dict["dependency"] == "neo4j"
    assert err_dict["retryable"] is True