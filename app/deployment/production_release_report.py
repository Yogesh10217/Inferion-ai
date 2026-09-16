from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.deployment.production_release_checklist import ProductionReleaseChecklistEvaluator
from app.deployment.production_smoke_test import ProductionSmokeTestPlanEvaluator
from app.deployment.release_governance import ProductionReleaseDecisionEngine
from app.deployment.secrets import SecretsSanitizer


@dataclass
class ProductionReleaseReport:
    report_title: str
    release_decision: str
    readiness_summary: Dict[str, Any]
    checklist_summary: Dict[str, Any]
    smoke_test_plan: Dict[str, Any]
    truthfulness_matrix: Dict[str, str]
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def sanitized_dict(self) -> Dict[str, Any]:
        return SecretsSanitizer.sanitize_structure({
            "report_title": self.report_title,
            "release_decision": self.release_decision,
            "readiness_summary": self.readiness_summary,
            "checklist_summary": self.checklist_summary,
            "smoke_test_plan": self.smoke_test_plan,
            "truthfulness_matrix": self.truthfulness_matrix,
            "generated_at": self.generated_at,
        })


class ProductionReleaseReportGenerator:
    """Generates the final canonical Production Release Certification Report."""

    @classmethod
    def generate_report(
        cls, external_evidence: Optional[Dict[str, Any]] = None
    ) -> ProductionReleaseReport:
        decision_engine = ProductionReleaseDecisionEngine()
        dec_res = decision_engine.evaluate_release_decision(external_evidence)

        checklist_res = ProductionReleaseChecklistEvaluator.evaluate_checklist()
        smoke_plan = ProductionSmokeTestPlanEvaluator.evaluate_smoke_test_plan()

        truthfulness_matrix = {
            "PRODUCTION_DEPLOYED": "NOT_EXECUTED",
            "PRODUCTION_DEPLOYMENT_VALIDATED": "NOT_EXECUTED",
            "PRODUCTION_RUNTIME_VALIDATED": "NOT_EXECUTED",
            "LIVE_PRODUCTION_VALIDATED": "NOT_EXECUTED",
            "LIVE_PRODUCTION": "NOT_EXECUTED",
            "PRODUCTION_DATABASE_MIGRATION_EXECUTED": "NOT_EXECUTED",
            "PRODUCTION_BACKUP_EXECUTED": "NOT_EXECUTED",
            "PRODUCTION_RESTORE_EXECUTED": "NOT_EXECUTED",
            "PRODUCTION_ROLLBACK_EXECUTED": "NOT_EXECUTED",
            "PRODUCTION_SMOKE_TEST_EXECUTED": "NOT_EXECUTED",
        }

        return ProductionReleaseReport(
            report_title="Phase 5.65 — Production Release Certification & Governance Report",
            release_decision=dec_res.decision.value,
            readiness_summary=dec_res.sanitized_dict(),
            checklist_summary=checklist_res.sanitized_dict(),
            smoke_test_plan=smoke_plan.sanitized_dict(),
            truthfulness_matrix=truthfulness_matrix,
        )
