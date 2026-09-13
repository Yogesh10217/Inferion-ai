from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from app.deployment.models import PlatformReadinessClassification
from app.deployment.secrets import SecretsSanitizer


class ApprovalCategory(str, Enum):
    TECHNICAL = "TECHNICAL"
    SECURITY = "SECURITY"
    DATABASE = "DATABASE"
    OPERATIONS = "OPERATIONS"
    RELEASE = "RELEASE"


class ApprovalStatus(str, Enum):
    NOT_REQUESTED = "NOT_REQUESTED"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    NOT_EXECUTED = "NOT_EXECUTED"


@dataclass
class ApprovalRequirement:
    category: ApprovalCategory
    approver_role: str
    required: bool = True
    status: ApprovalStatus = ApprovalStatus.PENDING
    approver_id: Optional[str] = None
    approved_at: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class ReleaseApprovalResult:
    status: str  # APPROVED, REJECTED, MANUAL_REVIEW_REQUIRED, NOT_EXECUTED
    requirements: List[ApprovalRequirement]
    classifications: List[str]
    evaluated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def sanitized_dict(self) -> Dict[str, Any]:
        return SecretsSanitizer.sanitize_structure({
            "status": self.status,
            "requirements": [
                {
                    "category": r.category.value,
                    "approver_role": r.approver_role,
                    "required": r.required,
                    "status": r.status.value,
                    "approver_id": r.approver_id,
                    "approved_at": r.approved_at,
                    "notes": r.notes,
                }
                for r in self.requirements
            ],
            "classifications": self.classifications,
            "evaluated_at": self.evaluated_at,
        })


class ReleaseApprovalEngine:
    """Structured approval governance for technical, security, database, operations, and release sign-offs."""

    @classmethod
    def create_default_approval_requirements(cls) -> List[ApprovalRequirement]:
        return [
            ApprovalRequirement(category=ApprovalCategory.TECHNICAL, approver_role="Lead Architect"),
            ApprovalRequirement(category=ApprovalCategory.SECURITY, approver_role="Security Officer"),
            ApprovalRequirement(category=ApprovalCategory.DATABASE, approver_role="Database Administrator"),
            ApprovalRequirement(category=ApprovalCategory.OPERATIONS, approver_role="Site Reliability Engineer"),
            ApprovalRequirement(category=ApprovalCategory.RELEASE, approver_role="Release Manager"),
        ]

    @classmethod
    def evaluate_approvals(
        cls, approvals: Optional[List[ApprovalRequirement]] = None, is_production: bool = False
    ) -> ReleaseApprovalResult:
        requirements = approvals or cls.create_default_approval_requirements()

        classifications = [
            PlatformReadinessClassification.RELEASE_APPROVAL_WORKFLOW_VALIDATED.value,
            "APPROVAL_RUNTIME_NOT_EXECUTED",
        ]

        any_rejected = any(r.status == ApprovalStatus.REJECTED for r in requirements)
        all_approved = all(r.status == ApprovalStatus.APPROVED for r in requirements if r.required)

        if any_rejected:
            status = "REJECTED"
        elif all_approved:
            status = "APPROVED"
        else:
            status = "MANUAL_REVIEW_REQUIRED"

        return ReleaseApprovalResult(
            status=status,
            requirements=requirements,
            classifications=classifications,
        )
