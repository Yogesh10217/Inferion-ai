"""
Cross-Phase Evidence Validation Engine.
Validates SHA-256 integrity, previous-hash linkage, and tamper protection across evidence records.
"""

import hashlib
import json
from typing import Dict, List, Tuple
from app.platform_hardening.exceptions import (
    CrossTenantPlatformHardeningException,
    EvidenceIntegrityException,
)
from app.platform_hardening.models import (
    CertificationEvidence,
    PlatformAuditFinding,
    PlatformAuditSeverity,
)


class CrossPhaseEvidenceValidationEngine:
    """Validates cryptographic integrity of SHA-256 evidence chains across audit records."""

    def validate_evidence_chain(
        self, records: List[Dict], tenant_id: str = "system"
    ) -> Tuple[bool, List[PlatformAuditFinding]]:
        findings: List[PlatformAuditFinding] = []
        prev_hash = None
        chain_valid = True

        for i, rec in enumerate(records):
            rec_tenant = rec.get("tenant_id")
            rec_hash = rec.get("sha256_hash")
            rec_prev_hash = rec.get("previous_hash")
            payload = rec.get("payload", {})

            # Check tenant isolation
            if rec_tenant and rec_tenant != tenant_id:
                findings.append(
                    PlatformAuditFinding(
                        finding_id=f"ev-tenant-leak-{i}",
                        tenant_id=tenant_id,
                        rule_id="RULE-EV-001",
                        title="Cross-Tenant Evidence Access Attempt",
                        description=f"Evidence item {i} belongs to tenant '{rec_tenant}', access attempted by '{tenant_id}'.",
                        severity=PlatformAuditSeverity.CRITICAL,
                        subsystem="evidence",
                        affected_component="EvidenceLedger",
                        remediation_suggestion="Enforce strict tenant boundary in evidence store.",
                    )
                )

            # Validate previous hash chain
            if i > 0 and prev_hash and rec_prev_hash != prev_hash:
                chain_valid = False
                findings.append(
                    PlatformAuditFinding(
                        finding_id=f"ev-chain-broken-{i}",
                        tenant_id=tenant_id,
                        rule_id="RULE-EV-002",
                        title="Evidence Hash Chain Broken",
                        description=f"Evidence item {i} previous_hash '{rec_prev_hash}' does not match prior hash '{prev_hash}'.",
                        severity=PlatformAuditSeverity.CRITICAL,
                        subsystem="evidence",
                        affected_component="EvidenceLedger",
                        root_cause_hypothesis="Evidence record was modified, deleted, or reordered.",
                        remediation_suggestion="Investigate evidence ledger for tampering.",
                    )
                )

            # Recompute SHA-256 hash if payload is present
            if payload and rec_hash:
                payload_str = json.dumps(payload, sort_keys=True)
                computed_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
                if computed_hash != rec_hash:
                    chain_valid = False
                    findings.append(
                        PlatformAuditFinding(
                            finding_id=f"ev-tampered-{i}",
                            tenant_id=tenant_id,
                            rule_id="RULE-EV-003",
                            title="Evidence Hash Tampering Detected",
                            description=f"Evidence item {i} recorded hash '{rec_hash}' does not match computed hash '{computed_hash}'.",
                            severity=PlatformAuditSeverity.CRITICAL,
                            subsystem="evidence",
                            affected_component="EvidenceLedger",
                            remediation_suggestion="Revert tampered evidence record and alert security control plane.",
                        )
                    )

            prev_hash = rec_hash

        return chain_valid, findings
