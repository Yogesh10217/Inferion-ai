from app.knowledge.lifecycle import DocumentState


def test_document_state_enum():
    assert DocumentState.ACTIVE.value == "ACTIVE"
    assert DocumentState.ARCHIVED.value == "ARCHIVED"
