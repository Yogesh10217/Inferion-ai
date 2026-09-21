from __future__ import annotations

from app.deployment.evidence_audit import RuntimeEvidenceAuditor
from app.deployment.models import EvidenceLevel


def test_evidence_auditor_phase_5_64():
    audit_res = RuntimeEvidenceAuditor.audit_phase_5_64_evidence()

    assert audit_res.claims_audited >= 5
    claim_names = [r.claim_name for r in audit_res.evidence_records]
    assert "CONTAINER_RESTART_RUNTIME_VALIDATED" in claim_names
    assert "CONTAINER_FAILURE_RUNTIME_VALIDATED" in claim_names
    assert "ROLLBACK_CONTAINER_RUNTIME_VALIDATED" in claim_names
    assert "PRODUCTION_DEPLOYED" in claim_names

    prod_claim = next(r for r in audit_res.evidence_records if r.claim_name == "PRODUCTION_DEPLOYED")
    assert prod_claim.status == "NOT_EXECUTED"
    assert prod_claim.evidence_level == EvidenceLevel.PRODUCTION_RUNTIME
