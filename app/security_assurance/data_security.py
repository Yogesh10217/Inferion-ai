"""Data Security Intelligence Engine."""

import uuid
from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, Field


class DataExfiltrationRiskAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"datasec-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    dataset_id: str
    sensitive_data_types: List[str] = Field(default_factory=list)
    exfiltration_risk_score: float = 10.0  # 0.0 to 100.0
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataSecurityEngine:
    """Evaluates data security posture and exfiltration risks."""

    def assess_dataset_security(
        self, tenant_id: str, dataset_id: str, sensitive_types: List[str]
    ) -> DataExfiltrationRiskAssessment:
        risk_score = min(100.0, len(sensitive_types) * 25.0)
        return DataExfiltrationRiskAssessment(
            tenant_id=tenant_id,
            dataset_id=dataset_id,
            sensitive_data_types=sensitive_types,
            exfiltration_risk_score=risk_score,
        )
