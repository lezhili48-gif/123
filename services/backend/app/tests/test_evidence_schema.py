from app.schemas.schemas import EvidenceItem


def test_evidence_schema_validation():
    obj = EvidenceItem(claim="x", source_pointer="10.1/y")
    assert obj.claim == "x"
