"""Data drift intelligence (Phase 5.43)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.data_intelligence.exceptions import CrossTenantDataIntelligenceException, DataDriftException


class DriftType(str, Enum):
    DISTRIBUTION_DRIFT = "DISTRIBUTION_DRIFT"
    SCHEMA_DRIFT = "SCHEMA_DRIFT"
    FEATURE_DRIFT = "FEATURE_DRIFT"
    CONCEPT_DRIFT_SIGNAL = "CONCEPT_DRIFT_SIGNAL"
    VOLUME_DRIFT = "VOLUME_DRIFT"
    QUALITY_DRIFT = "QUALITY_DRIFT"


class DriftSeverity(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    SEVERE = "SEVERE"


class DataDrift(BaseModel):
    drift_id: str
    dataset_id: str
    tenant_id: str
    drift_type: DriftType
    severity: DriftSeverity
    drift_score: float
    feature_name: Optional[str] = None
    baseline_reference: str
    current_reference: str
    details: Dict[str, Any] = Field(default_factory=dict)
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DriftAssessment(BaseModel):
    assessment_id: str
    dataset_id: str
    tenant_id: str
    overall_drift_detected: bool
    max_drift_score: float
    drifts: List[DataDrift] = Field(default_factory=list)
    summary: str
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataDriftManager:
    """Manages dataset drift detection and assessments."""

    def __init__(self) -> None:
        self._drifts: Dict[str, DataDrift] = {}
        self._assessments: Dict[str, DriftAssessment] = {}

    def detect_drift(
        self,
        dataset_id: str,
        tenant_id: str,
        drift_type: DriftType,
        drift_score: float,
        baseline_reference: str = "baseline-v1",
        current_reference: str = "current-v1",
        feature_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        drift_id: Optional[str] = None,
    ) -> DataDrift:
        did = drift_id or f"drift-{uuid.uuid4().hex[:8]}"
        sev = DriftSeverity.NONE
        if drift_score >= 0.7:
            sev = DriftSeverity.SEVERE
        elif drift_score >= 0.5:
            sev = DriftSeverity.HIGH
        elif drift_score >= 0.3:
            sev = DriftSeverity.MODERATE
        elif drift_score > 0.1:
            sev = DriftSeverity.LOW

        drift = DataDrift(
            drift_id=did,
            dataset_id=dataset_id,
            tenant_id=tenant_id,
            drift_type=drift_type,
            severity=sev,
            drift_score=round(drift_score, 4),
            feature_name=feature_name,
            baseline_reference=baseline_reference,
            current_reference=current_reference,
            details=details or {},
        )
        self._drifts[did] = drift
        return drift

    def evaluate_drift_assessment(self, dataset_id: str, tenant_id: str) -> DriftAssessment:
        drifts = [d for d in self._drifts.values() if d.dataset_id == dataset_id and d.tenant_id == tenant_id]
        aid = f"da-{uuid.uuid4().hex[:8]}"

        max_score = max([d.drift_score for d in drifts], default=0.0)
        has_drift = max_score >= 0.3 or any(d.severity in (DriftSeverity.HIGH, DriftSeverity.SEVERE) for d in drifts)

        ass = DriftAssessment(
            assessment_id=aid,
            dataset_id=dataset_id,
            tenant_id=tenant_id,
            overall_drift_detected=has_drift,
            max_drift_score=max_score,
            drifts=drifts,
            summary=f"Drift assessment for dataset {dataset_id}: detected={has_drift}, max_score={max_score:.2f}, count={len(drifts)}",
        )
        self._assessments[aid] = ass
        return ass

    def get_drift(self, drift_id: str, tenant_id: str) -> DataDrift:
        d = self._drifts.get(drift_id)
        if not d:
            raise DataDriftException(f"Drift '{drift_id}' not found.")
        if d.tenant_id != tenant_id:
            raise CrossTenantDataIntelligenceException()
        return d
