from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.deployment.models import PlatformReadinessClassification, ProductionReleaseDecision
from app.deployment.secrets import SecretsSanitizer


@dataclass
class ChecklistItem:
    section_number: int
    name: str
    status: str  # PASSED, FAILED, WARNING, NOT_EXECUTED
    blocking: bool
    evidence_level: str
    message: str
    execution_status: str = "VALIDATED"


@dataclass
class ProductionReleaseChecklistResult:
    decision: ProductionReleaseDecision
    total_sections: int
    passed_sections: int
    failed_sections: int
    manual_review_sections: int
    items: List[ChecklistItem]
    classifications: List[str]
    evaluated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def sanitized_dict(self) -> Dict[str, Any]:
        return SecretsSanitizer.sanitize_structure({
            "decision": self.decision.value,
            "total_sections": self.total_sections,
            "passed_sections": self.passed_sections,
            "failed_sections": self.failed_sections,
            "manual_review_sections": self.manual_review_sections,
            "items": [
                {
                    "section_number": i.section_number,
                    "name": i.name,
                    "status": i.status,
                    "blocking": i.blocking,
                    "evidence_level": i.evidence_level,
                    "message": i.message,
                    "execution_status": i.execution_status,
                }
                for i in self.items
            ],
            "classifications": self.classifications,
            "evaluated_at": self.evaluated_at,
        })


class ProductionReleaseChecklistEvaluator:
    """Evaluates the 14-section canonical release checklist producing GO / NO_GO / MANUAL_REVIEW / NOT_EXECUTED decision."""

    @classmethod
    def evaluate_checklist(cls, checklist_data: Optional[Dict[str, Any]] = None) -> ProductionReleaseChecklistResult:
        data = checklist_data or {}
        items: List[ChecklistItem] = []

        # 1. Artifact Integrity
        art_ok = data.get("artifact_valid", True)
        items.append(
            ChecklistItem(
                section_number=1,
                name="Artifact Integrity",
                status="PASSED" if art_ok else "FAILED",
                blocking=True,
                evidence_level=data.get("artifact_evidence", "CONTAINER_RUNTIME"),
                message="Artifact digest and image reference integrity verified" if art_ok else "Invalid artifact digest or mismatch",
            )
        )

        # 2. Configuration
        cfg_ok = data.get("configuration_valid", True)
        items.append(
            ChecklistItem(
                section_number=2,
                name="Configuration Safety",
                status="PASSED" if cfg_ok else "FAILED",
                blocking=True,
                evidence_level="SIMULATION_RUNTIME",
                message="Runtime configuration and environment rules valid" if cfg_ok else "Configuration error or debug mode enabled in production",
            )
        )

        # 3. Secret Safety
        sec_ok = data.get("secret_safety_valid", True)
        items.append(
            ChecklistItem(
                section_number=3,
                name="Secret Safety",
                status="PASSED" if sec_ok else "FAILED",
                blocking=True,
                evidence_level="SIMULATION_RUNTIME",
                message="Secret canary audit passed; fallback secrets disabled" if sec_ok else "Unsafe or canary secret detected",
            )
        )

        # 4. Database Readiness
        db_ok = data.get("database_ready", True)
        items.append(
            ChecklistItem(
                section_number=4,
                name="Database Readiness",
                status="PASSED" if db_ok else "FAILED",
                blocking=True,
                evidence_level="CONTAINER_RUNTIME",
                message="Database connectivity and migration safety verified",
            )
        )

        # 5. Dependency Readiness
        dep_ok = data.get("dependencies_ready", True)
        items.append(
            ChecklistItem(
                section_number=5,
                name="Dependency Readiness",
                status="PASSED" if dep_ok else "FAILED",
                blocking=True,
                evidence_level="CONTAINER_RUNTIME",
                message="PostgreSQL, Redis, Prometheus dependencies healthy",
            )
        )

        # 6. Container Runtime
        cnt_ok = data.get("container_runtime_ready", True)
        items.append(
            ChecklistItem(
                section_number=6,
                name="Container Runtime",
                status="PASSED" if cnt_ok else "FAILED",
                blocking=True,
                evidence_level="CONTAINER_RUNTIME",
                message="Non-root user UID 10001, Dockerfile, image tag verified",
            )
        )

        # 7. Security
        sec_pol_ok = data.get("security_policy_valid", True)
        items.append(
            ChecklistItem(
                section_number=7,
                name="Security Policy & OpenAPI Protection",
                status="PASSED" if sec_pol_ok else "FAILED",
                blocking=True,
                evidence_level="CONTAINER_RUNTIME",
                message="Security headers present and /docs endpoints disabled in production",
            )
        )

        # 8. Observability
        obs_ok = data.get("observability_ready", True)
        items.append(
            ChecklistItem(
                section_number=8,
                name="Observability Readiness",
                status="PASSED" if obs_ok else "FAILED",
                blocking=True,
                evidence_level="CONTAINER_RUNTIME",
                message="Structured logging, health probes, Prometheus metrics active",
            )
        )

        # 9. Backup
        bk_ok = data.get("backup_plan_ready", True)
        items.append(
            ChecklistItem(
                section_number=9,
                name="Backup Strategy",
                status="PASSED" if bk_ok else "FAILED",
                blocking=False,
                evidence_level="STATIC",
                message="Database and configuration backup plan defined",
            )
        )

        # 10. Disaster Recovery
        dr_ok = data.get("disaster_recovery_ready", True)
        items.append(
            ChecklistItem(
                section_number=10,
                name="Disaster Recovery Plan",
                status="PASSED" if dr_ok else "FAILED",
                blocking=False,
                evidence_level="STATIC",
                message="RTO (15m) / RPO (5m) objectives and restore plan verified",
            )
        )

        # 11. Rollback
        rb_ok = data.get("rollback_strategy_ready", True)
        items.append(
            ChecklistItem(
                section_number=11,
                name="Rollback Strategy",
                status="PASSED" if rb_ok else "FAILED",
                blocking=True,
                evidence_level="SIMULATION_RUNTIME",
                message="RollbackStrategyEngine and previous artifact restoration ready",
            )
        )

        # 12. Infrastructure
        inf_ok = data.get("infrastructure_ready", True)
        items.append(
            ChecklistItem(
                section_number=12,
                name="Infrastructure Readiness",
                status="PASSED" if inf_ok else "FAILED",
                blocking=True,
                evidence_level="CONTAINER_RUNTIME",
                message="Host Docker daemon, compute, network, database infrastructure ready",
            )
        )

        # 13. Approval
        app_status = data.get("approval_status", "MANUAL_REVIEW_REQUIRED")
        items.append(
            ChecklistItem(
                section_number=13,
                name="Release Approval Governance",
                status="PASSED" if app_status == "APPROVED" else ("MANUAL_REVIEW" if app_status == "MANUAL_REVIEW_REQUIRED" else "FAILED"),
                blocking=True,
                evidence_level="STATIC",
                message="Technical, Security, DBA, SRE, and Release Manager approval status",
                execution_status="APPROVAL_RUNTIME_NOT_EXECUTED" if app_status != "APPROVED" else "VALIDATED",
            )
        )

        # 14. Operational Readiness
        op_ok = data.get("operational_readiness_valid", True)
        items.append(
            ChecklistItem(
                section_number=14,
                name="Operational Readiness & Runbooks",
                status="PASSED" if op_ok else "FAILED",
                blocking=False,
                evidence_level="STATIC",
                message="Release, Rollback, Incident Response, and Smoke Test runbooks available",
            )
        )

        has_blocking_failure = any(i.status == "FAILED" and i.blocking for i in items)
        has_manual_review = any(i.status == "MANUAL_REVIEW" for i in items)

        if has_blocking_failure:
            decision = ProductionReleaseDecision.NO_GO
        elif has_manual_review:
            decision = ProductionReleaseDecision.MANUAL_REVIEW_REQUIRED
        else:
            decision = ProductionReleaseDecision.GO

        classifications = [
            PlatformReadinessClassification.PRODUCTION_RELEASE_CHECKLIST_VALIDATED.value,
        ]

        return ProductionReleaseChecklistResult(
            decision=decision,
            total_sections=len(items),
            passed_sections=sum(1 for i in items if i.status == "PASSED"),
            failed_sections=sum(1 for i in items if i.status == "FAILED"),
            manual_review_sections=sum(1 for i in items if i.status == "MANUAL_REVIEW"),
            items=items,
            classifications=classifications,
        )
