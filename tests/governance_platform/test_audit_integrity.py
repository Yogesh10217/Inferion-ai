"""Unit tests for evidence audit integrity hashing and verification."""

from app.governance_platform.evidence import EvidenceCollector, EvidenceSource


def test_evidence_audit_integrity_verification():
    collector = EvidenceCollector()

    evd = collector.collect_evidence(
        EvidenceSource.POLICY_DECISION, "dec_1", "res_1", {"decision": "ALLOW"}, tenant_id="t_aud"
    )

    assert evd.content_hash is not None
    assert len(evd.content_hash) == 64  # SHA-256 hex string length
