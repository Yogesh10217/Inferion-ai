"""
Platform Certification Engine.
Evaluates multi-tier platform certification (FAILED, BLOCKED, PARTIAL, CERTIFIED, PRODUCTION_READY) and seals evidence.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from app.platform_hardening.models import (
    CertificationEvidence,
    PlatformAuditFinding,
    PlatformCertification,
    PlatformCertificationStatus,
    ReleaseGateResult,
    ReleaseReadinessDecision,
)


class PlatformCertificationEngine:
    """Evaluates multi-tier platform certification status and generates cryptographic evidence."""

    def certify_platform(
        self,
        tenant_id: str,
        audit_id: str,
        readiness_score: float,
        release_gate: ReleaseGateResult,
        findings: List[PlatformAuditFinding],
        previous_hash: Optional[str] = None,
    ) -> PlatformCertification:

        # Determine Multi-Tier Certification Status
        if release_gate.decision == ReleaseReadinessDecision.BLOCKED:
            status = PlatformCertificationStatus.BLOCKED
        elif readiness_score < 50.0:
            status = PlatformCertificationStatus.FAILED
        elif readiness_score < 80.0 or any(f.severity.value in ["HIGH", "CRITICAL"] for f in findings):
            status = PlatformCertificationStatus.PARTIAL
        elif readiness_score >= 90.0 and len(findings) == 0:
            status = PlatformCertificationStatus.PRODUCTION_READY
        else:
            status = PlatformCertificationStatus.CERTIFIED

        cert_id = f"cert-{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)

        # Generate Cryptographic Evidence Hash
        payload = {
            "certification_id": cert_id,
            "tenant_id": tenant_id,
            "audit_id": audit_id,
            "status": status.value,
            "release_decision": release_gate.decision.value,
            "readiness_score": readiness_score,
            "certified_at": now.isoformat(),
        }
        payload_str = json.dumps(payload, sort_keys=True)
        sha256_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

        evidence = CertificationEvidence(
            evidence_id=f"ev-{cert_id}",
            tenant_id=tenant_id,
            audit_id=audit_id,
            sha256_hash=sha256_hash,
            previous_hash=previous_hash,
            sealed_at=now,
            is_valid=True,
        )

        return PlatformCertification(
            certification_id=cert_id,
            tenant_id=tenant_id,
            status=status,
            release_decision=release_gate.decision,
            overall_score=readiness_score,
            evidence=evidence,
            audited_phases_count=8,
            certified_at=now,
            details={"release_gate_reason": release_gate.reason, "findings_count": len(findings)},
        )
