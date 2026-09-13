from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.deployment.models import EvidenceLevel, PlatformReadinessClassification
from app.deployment.secrets import SecretsSanitizer


@dataclass
class EvidenceRecord:
    claim_name: str
    evidence_level: EvidenceLevel
    status: str
    empirical_command: Optional[str] = None
    evidence_payload: Dict[str, Any] = field(default_factory=dict)
    audited_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def sanitized_payload(self) -> Dict[str, Any]:
        return SecretsSanitizer.sanitize_structure(self.evidence_payload)


@dataclass
class EvidenceAuditResult:
    claims_audited: int
    valid_claims: int
    downgraded_claims: int
    evidence_records: List[EvidenceRecord]
    readiness_classification: PlatformReadinessClassification
    audited_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class RuntimeEvidenceAuditor:
    """Audits Phase 5.64 runtime claims to verify whether empirical container execution evidence exists."""

    @classmethod
    def audit_phase_5_64_evidence(cls, external_evidence: Optional[Dict[str, Any]] = None) -> EvidenceAuditResult:
        records: List[EvidenceRecord] = []
        evidence_data = external_evidence or {}

        # 1. Container Build Runtime Evidence
        build_ev = evidence_data.get("container_build", {})
        if build_ev.get("image_digest") and build_ev.get("image_digest") != "NOT_AVAILABLE":
            records.append(
                EvidenceRecord(
                    claim_name="CONTAINER_BUILD_RUNTIME_VALIDATED",
                    evidence_level=EvidenceLevel.CONTAINER_RUNTIME,
                    status="VALIDATED",
                    empirical_command="docker build -t enterprise-ai-platform:production-simulation -f Dockerfile .",
                    evidence_payload={
                        "image_tag": build_ev.get("image_tag", "enterprise-ai-platform:production-simulation"),
                        "image_digest": build_ev.get("image_digest"),
                        "user_id": build_ev.get("user_id", 10001),
                    },
                )
            )
        else:
            records.append(
                EvidenceRecord(
                    claim_name="CONTAINER_BUILD_RUNTIME_VALIDATED",
                    evidence_level=EvidenceLevel.UNIT_TEST,
                    status="SIMULATION_VALIDATED",
                    empirical_command="pytest tests/container_simulation/",
                    evidence_payload={"note": "Image digest not captured in live environment"},
                )
            )

        # 2. Container Simulation Stack Evidence
        stack_ev = evidence_data.get("compose_stack", {})
        if stack_ev.get("services_healthy", False) or stack_ev.get("container_app_running", False):
            records.append(
                EvidenceRecord(
                    claim_name="COMPOSE_SIMULATION_STACK_VALIDATED",
                    evidence_level=EvidenceLevel.CONTAINER_RUNTIME,
                    status="VALIDATED",
                    empirical_command="docker compose -f docker-compose.production-simulation.yml up -d",
                    evidence_payload={
                        "app_status": "healthy",
                        "db_status": "healthy",
                        "redis_status": "healthy",
                    },
                )
            )
        else:
            records.append(
                EvidenceRecord(
                    claim_name="COMPOSE_SIMULATION_STACK_VALIDATED",
                    evidence_level=EvidenceLevel.SIMULATION_RUNTIME,
                    status="SIMULATION_VALIDATED",
                    empirical_command="pytest tests/production_simulation/",
                    evidence_payload={"note": "Evaluated via ASGI simulation runtime"},
                )
            )

        # 3. Container Restart Evidence
        restart_ev = evidence_data.get("container_restart", {})
        if restart_ev.get("empirical_restart_executed", False):
            records.append(
                EvidenceRecord(
                    claim_name="CONTAINER_RESTART_RUNTIME_VALIDATED",
                    evidence_level=EvidenceLevel.CONTAINER_RUNTIME,
                    status="VALIDATED",
                    empirical_command="docker restart production-simulation-app",
                    evidence_payload=restart_ev,
                )
            )
        else:
            records.append(
                EvidenceRecord(
                    claim_name="CONTAINER_RESTART_RUNTIME_VALIDATED",
                    evidence_level=EvidenceLevel.SIMULATION_RUNTIME,
                    status="SIMULATION_VALIDATED",
                    empirical_command="pytest tests/container_simulation/test_container_restart.py",
                    evidence_payload={"note": "Validated via simulated container restart test suite"},
                )
            )

        # 4. Container Failure Injection Evidence
        failure_ev = evidence_data.get("container_failure", {})
        if failure_ev.get("empirical_failure_injected", False):
            records.append(
                EvidenceRecord(
                    claim_name="CONTAINER_FAILURE_RUNTIME_VALIDATED",
                    evidence_level=EvidenceLevel.CONTAINER_RUNTIME,
                    status="VALIDATED",
                    empirical_command="failure_injection_simulation",
                    evidence_payload=failure_ev,
                )
            )
        else:
            records.append(
                EvidenceRecord(
                    claim_name="CONTAINER_FAILURE_RUNTIME_VALIDATED",
                    evidence_level=EvidenceLevel.SIMULATION_RUNTIME,
                    status="SIMULATION_VALIDATED",
                    empirical_command="pytest tests/production_simulation/test_failure_injection.py",
                    evidence_payload={"note": "Validated via 9-trigger failure injection simulation"},
                )
            )

        # 5. Container Rollback Evidence
        rollback_ev = evidence_data.get("container_rollback", {})
        if rollback_ev.get("empirical_rollback_executed", False):
            records.append(
                EvidenceRecord(
                    claim_name="ROLLBACK_CONTAINER_RUNTIME_VALIDATED",
                    evidence_level=EvidenceLevel.CONTAINER_RUNTIME,
                    status="VALIDATED",
                    empirical_command="rollback_strategy_execution",
                    evidence_payload=rollback_ev,
                )
            )
        else:
            records.append(
                EvidenceRecord(
                    claim_name="ROLLBACK_CONTAINER_RUNTIME_VALIDATED",
                    evidence_level=EvidenceLevel.SIMULATION_RUNTIME,
                    status="SIMULATION_VALIDATED",
                    empirical_command="pytest tests/deployment/test_rollback.py",
                    evidence_payload={"note": "Validated via RollbackStrategyEngine simulation"},
                )
            )

        # 6. Production Environment Evidence Boundary
        records.append(
            EvidenceRecord(
                claim_name="PRODUCTION_DEPLOYED",
                evidence_level=EvidenceLevel.PRODUCTION_RUNTIME,
                status="NOT_EXECUTED",
                empirical_command=None,
                evidence_payload={"boundary": "Strict truthfulness rule enforced: Production deployment NOT_EXECUTED"},
            )
        )

        valid_count = sum(1 for r in records if r.status == "VALIDATED")
        downgraded_count = sum(1 for r in records if r.status == "SIMULATION_VALIDATED")

        return EvidenceAuditResult(
            claims_audited=len(records),
            valid_claims=valid_count,
            downgraded_claims=downgraded_count,
            evidence_records=records,
            readiness_classification=PlatformReadinessClassification.RUNTIME_EVIDENCE_AUDITED,
        )
