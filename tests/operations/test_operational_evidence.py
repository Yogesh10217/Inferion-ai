from app.operations.operational_evidence import OperationalEvidenceCollector


def test_operational_evidence_fingerprint():
    collector = OperationalEvidenceCollector()
    raw_payload = {"service": "enterprise-ai-platform", "status": "HEALTHY", "secret_key": "my_secret_token"}
    ev = collector.create_evidence(raw_payload, evidence_level="CONTAINER_RUNTIME")

    assert ev.evidence_id == "ev-568-001"
    assert len(ev.sha256_fingerprint) == 64
    # Verify secret is sanitized in evidence
    assert "my_secret_token" not in str(ev.canonical_payload)
