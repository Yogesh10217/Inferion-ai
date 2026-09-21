"""Unit tests for automated SecretManager secret redaction in evidence payloads."""

from app.governance_platform.evidence import EvidenceCollector, EvidenceSource


def test_secret_redaction_in_evidence_payload():
    collector = EvidenceCollector()

    payload = {"api_key": "sk-proj-1234567890abcdef1234567890", "normal_field": "public_info"}
    evd = collector.collect_evidence(EvidenceSource.AUDIT_LOG, "rec_1", "res_1", payload, tenant_id="t_sec")

    assert "sk-proj-1234567890abcdef1234567890" not in evd.payload["api_key"]
    assert "[REDACTED_SECRET]" in evd.payload["api_key"] or "sk-" not in evd.payload["api_key"]
