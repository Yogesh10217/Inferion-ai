"""Integration Data Governance Coordination (Phase 5.40)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.integration_intelligence.exceptions import CrossTenantIntegrationAccessException


class IntegrationDataClassification(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"
    PII_FINANCIAL = "PII_FINANCIAL"


class IntegrationDataAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"data_asm_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    workflow_id: str
    classification: IntegrationDataClassification = IntegrationDataClassification.INTERNAL
    has_cross_border_transfer: bool = False
    transfer_permitted: bool = True
    retention_policy_id: Optional[str] = None
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IntegrationDataGovernanceManager:
    """Composes with data_governance to evaluate data classification & transfer rules."""

    def __init__(self) -> None:
        self._assessments: Dict[str, IntegrationDataAssessment] = {}

    def evaluate_data_flow(
        self,
        tenant_id: str,
        workflow_id: str,
        classification: IntegrationDataClassification = IntegrationDataClassification.INTERNAL,
        has_cross_border_transfer: bool = False,
    ) -> IntegrationDataAssessment:
        permitted = not (classification == IntegrationDataClassification.RESTRICTED and has_cross_border_transfer)
        asm = IntegrationDataAssessment(
            tenant_id=tenant_id,
            workflow_id=workflow_id,
            classification=classification,
            has_cross_border_transfer=has_cross_border_transfer,
            transfer_permitted=permitted,
            retention_policy_id="ret_policy_std_90d",
        )
        self._assessments[asm.assessment_id] = asm
        return asm

    def get_assessment(self, tenant_id: str, assessment_id: str) -> IntegrationDataAssessment:
        asm = self._assessments.get(assessment_id)
        if not asm or asm.tenant_id != tenant_id:
            raise CrossTenantIntegrationAccessException()
        return asm
