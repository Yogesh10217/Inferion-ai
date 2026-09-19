"""Model Drift Intelligence (Phase 5.44)."""

import hashlib
import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.model_intelligence.exceptions import CrossTenantModelIntelligenceException, ModelDriftNotFoundException

logger = logging.getLogger(__name__)


class ModelDriftType(str, Enum):
    PERFORMANCE_DRIFT = "PERFORMANCE_DRIFT"
    BEHAVIORAL_DRIFT = "BEHAVIORAL_DRIFT"
    DATA_DISTRIBUTION_DRIFT = "DATA_DISTRIBUTION_DRIFT"
    OUTPUT_DISTRIBUTION_DRIFT = "OUTPUT_DISTRIBUTION_DRIFT"
    PROVIDER_BEHAVIOR_DRIFT = "PROVIDER_BEHAVIOR_DRIFT"


class DriftSeverity(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    SEVERE = "SEVERE"


class DriftEvidence(BaseModel):
    evidence_id: str
    baseline_fingerprint: str
    current_fingerprint: str
    drift_score: float  # e.g. 0.05
    data_intelligence_ref: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelDrift(BaseModel):
    drift_id: str
    model_id: str
    tenant_id: str
    drift_type: ModelDriftType
    severity: DriftSeverity
    drift_score: float
    evidence: DriftEvidence
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DriftAssessment(BaseModel):
    assessment_id: str
    model_id: str
    tenant_id: str
    overall_drift_severity: DriftSeverity
    active_drifts: List[ModelDrift] = Field(default_factory=list)
    requires_remediation: bool = False
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelDriftManager:
    """Manages model drift detection and intelligence integration with data_intelligence."""

    def __init__(self) -> None:
        self._drifts: Dict[str, ModelDrift] = {}

    def detect_drift(
        self,
        model_id: str,
        tenant_id: str,
        drift_type: ModelDriftType,
        drift_score: float,
        data_intelligence_ref: Optional[str] = None,
    ) -> ModelDrift:
        d_id = f"drift-{uuid.uuid4().hex[:8]}"

        sev = (
            DriftSeverity.NONE
            if drift_score < 0.05
            else (
                DriftSeverity.LOW
                if drift_score < 0.15
                else (
                    DriftSeverity.MEDIUM
                    if drift_score < 0.3
                    else (DriftSeverity.HIGH if drift_score < 0.5 else DriftSeverity.SEVERE)
                )
            )
        )

        base_fp = hashlib.sha256(f"baseline:{model_id}:{tenant_id}".encode()).hexdigest()
        curr_fp = hashlib.sha256(f"current:{model_id}:{tenant_id}:{drift_score}".encode()).hexdigest()

        evidence = DriftEvidence(
            evidence_id=f"devid-{uuid.uuid4().hex[:6]}",
            baseline_fingerprint=base_fp,
            current_fingerprint=curr_fp,
            drift_score=drift_score,
            data_intelligence_ref=data_intelligence_ref,
        )

        drift = ModelDrift(
            drift_id=d_id,
            model_id=model_id,
            tenant_id=tenant_id,
            drift_type=drift_type,
            severity=sev,
            drift_score=drift_score,
            evidence=evidence,
        )

        self._drifts[d_id] = drift
        logger.info(f"[MODEL DRIFT] Detected {drift_type} for model {model_id} (Tenant: {tenant_id}) Severity: {sev}")
        return drift

    def assess_model_drift(self, model_id: str, tenant_id: str) -> DriftAssessment:
        drifts = [d for d in self._drifts.values() if d.model_id == model_id and d.tenant_id == tenant_id]
        if not drifts:
            return DriftAssessment(
                assessment_id=f"dassess-{uuid.uuid4().hex[:8]}",
                model_id=model_id,
                tenant_id=tenant_id,
                overall_drift_severity=DriftSeverity.NONE,
                requires_remediation=False,
            )

        max_sev = max(d.severity for d in drifts)
        req_rem = max_sev in [DriftSeverity.HIGH, DriftSeverity.SEVERE]

        return DriftAssessment(
            assessment_id=f"dassess-{uuid.uuid4().hex[:8]}",
            model_id=model_id,
            tenant_id=tenant_id,
            overall_drift_severity=max_sev,
            active_drifts=drifts,
            requires_remediation=req_rem,
        )

    def get_drift(self, drift_id: str, tenant_id: str) -> ModelDrift:
        d = self._drifts.get(drift_id)
        if not d:
            raise ModelDriftNotFoundException(f"Drift record '{drift_id}' not found.")
        if d.tenant_id != tenant_id:
            raise CrossTenantModelIntelligenceException()
        return d
