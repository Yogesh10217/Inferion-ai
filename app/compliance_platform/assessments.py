"""Compliance Assessment Engine & Control Evaluation Subsystem."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.compliance_platform.controls import ControlManager, ControlStatus
from app.compliance_platform.evidence import EvidenceManager, EvidenceStatus
from app.compliance_platform.exceptions import ComplianceAssessmentException
from app.compliance_platform.frameworks import FrameworkManager
from app.compliance_platform.requirements import RequirementManager


class AssessmentResult(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class AssessmentStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AssessmentMethod(str, Enum):
    AUTOMATED = "AUTOMATED"
    MANUAL = "MANUAL"
    HYBRID = "HYBRID"


class ControlAssessment(BaseModel):
    control_id: str
    control_code: str
    result: AssessmentResult
    evidence_ids: List[str] = Field(default_factory=list)
    explanation: str


class RequirementAssessment(BaseModel):
    requirement_id: str
    requirement_code: str
    result: AssessmentResult
    control_assessments: List[ControlAssessment] = Field(default_factory=list)
    explanation: str


class ComplianceAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"assess_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    framework_id: str
    status: AssessmentStatus = AssessmentStatus.COMPLETED
    overall_result: AssessmentResult = AssessmentResult.INSUFFICIENT_EVIDENCE
    requirement_assessments: List[RequirementAssessment] = Field(default_factory=list)
    total_evaluated_requirements: int = 0
    passed_count: int = 0
    failed_count: int = 0
    insufficient_evidence_count: int = 0
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ComplianceAssessmentManager:
    """Evaluates compliance status strictly based on collected evidence."""

    def __init__(
        self,
        framework_manager: FrameworkManager,
        requirement_manager: RequirementManager,
        control_manager: ControlManager,
        evidence_manager: EvidenceManager,
    ) -> None:
        self.framework_manager = framework_manager
        self.requirement_manager = requirement_manager
        self.control_manager = control_manager
        self.evidence_manager = evidence_manager
        self._assessments: Dict[str, ComplianceAssessment] = {}

    def run_assessment(self, tenant_id: str, framework_id: str, subject_id: str = "global") -> ComplianceAssessment:
        fw = self.framework_manager.get_framework(framework_id, tenant_id)
        reqs = self.requirement_manager.list_requirements(tenant_id, framework_id)
        ctrls = self.control_manager.list_controls(tenant_id)
        evidence_list = self.evidence_manager.list_evidence_for_subject(tenant_id, subject_id)

        req_assessments: List[RequirementAssessment] = []
        passed_cnt = 0
        failed_cnt = 0
        insufficient_cnt = 0

        for r in reqs:
            # Find controls mapped to this requirement
            mapped_ctrls = [
                c
                for c in ctrls
                if r.requirement_id in c.requirement_ids or r.code in c.name or len(c.requirement_ids) == 0
            ]

            ctrl_assessments: List[ControlAssessment] = []
            for c in mapped_ctrls:
                # Find matching valid evidence
                matching_ev = [e for e in evidence_list if e.status == EvidenceStatus.VALID]

                if c.status == ControlStatus.FAILED:
                    c_res = AssessmentResult.FAIL
                    c_expl = f"Control '{c.code}' is marked FAILED in operational monitoring."
                elif not matching_ev:
                    c_res = AssessmentResult.INSUFFICIENT_EVIDENCE
                    c_expl = f"Control '{c.code}' has no valid evidence submitted."
                else:
                    c_res = AssessmentResult.PASS
                    c_expl = f"Control '{c.code}' verified with {len(matching_ev)} valid evidence item(s)."

                ctrl_assessments.append(
                    ControlAssessment(
                        control_id=c.control_id,
                        control_code=c.code,
                        result=c_res,
                        evidence_ids=[e.evidence_id for e in matching_ev],
                        explanation=c_expl,
                    )
                )

            # Determine overall requirement result
            if any(ca.result == AssessmentResult.FAIL for ca in ctrl_assessments):
                req_res = AssessmentResult.FAIL
                failed_cnt += 1
                req_expl = f"Requirement '{r.code}' failed due to control failures."
            elif (
                any(ca.result == AssessmentResult.INSUFFICIENT_EVIDENCE for ca in ctrl_assessments)
                or not ctrl_assessments
            ):
                req_res = AssessmentResult.INSUFFICIENT_EVIDENCE
                insufficient_cnt += 1
                req_expl = f"Requirement '{r.code}' cannot pass due to insufficient evidence."
            else:
                req_res = AssessmentResult.PASS
                passed_cnt += 1
                req_expl = f"Requirement '{r.code}' satisfied by controls and evidence."

            req_assessments.append(
                RequirementAssessment(
                    requirement_id=r.requirement_id,
                    requirement_code=r.code,
                    result=req_res,
                    control_assessments=ctrl_assessments,
                    explanation=req_expl,
                )
            )

        if failed_cnt > 0:
            overall = AssessmentResult.FAIL
        elif insufficient_cnt > 0:
            overall = AssessmentResult.INSUFFICIENT_EVIDENCE
        else:
            overall = AssessmentResult.PASS if passed_cnt > 0 else AssessmentResult.NOT_APPLICABLE

        assessment = ComplianceAssessment(
            tenant_id=tenant_id,
            framework_id=framework_id,
            status=AssessmentStatus.COMPLETED,
            overall_result=overall,
            requirement_assessments=req_assessments,
            total_evaluated_requirements=len(reqs),
            passed_count=passed_cnt,
            failed_count=failed_cnt,
            insufficient_evidence_count=insufficient_cnt,
        )
        self._assessments[assessment.assessment_id] = assessment
        return assessment

    def get_assessment(self, assessment_id: str, tenant_id: str) -> ComplianceAssessment:
        ass = self._assessments.get(assessment_id)
        if not ass or ass.tenant_id != tenant_id:
            raise ComplianceAssessmentException(f"Assessment '{assessment_id}' not found for tenant '{tenant_id}'.")
        return ass
