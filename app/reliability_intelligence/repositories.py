"""Thread-safe tenant-isolated repositories for Reliability Intelligence (Phase 5.55)."""

import threading
from typing import Dict, List, Optional

from app.reliability_intelligence.exceptions import (
    CrossTenantReliabilityIntelligenceException,
    FailurePredictionNotFoundException,
    ReliabilityAssessmentNotFoundException,
    ServiceHealthNotFoundException,
)
from app.reliability_intelligence.models import (
    FailurePrediction,
    ReliabilityAssessment,
    ReliabilityEvidenceBundle,
    ServiceHealthAssessment,
    ServiceLevelObjective,
)


class ServiceHealthRepository:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._storage: Dict[str, ServiceHealthAssessment] = {}

    def save(self, sh: ServiceHealthAssessment) -> ServiceHealthAssessment:
        with self._lock:
            self._storage[sh.assessment_id] = sh
            return sh

    def get_by_id(self, tenant_id: str, assessment_id: str) -> ServiceHealthAssessment:
        with self._lock:
            sh = self._storage.get(assessment_id)
            if not sh:
                raise ServiceHealthNotFoundException(assessment_id)
            if sh.tenant_id != tenant_id:
                raise CrossTenantReliabilityIntelligenceException()
            return sh

    def list_by_tenant(self, tenant_id: str) -> List[ServiceHealthAssessment]:
        with self._lock:
            return [s for s in self._storage.values() if s.tenant_id == tenant_id]


class ReliabilityAssessmentRepository:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._storage: Dict[str, ReliabilityAssessment] = {}

    def save(self, assessment: ReliabilityAssessment) -> ReliabilityAssessment:
        with self._lock:
            self._storage[assessment.assessment_id] = assessment
            return assessment

    def get_by_id(self, tenant_id: str, assessment_id: str) -> ReliabilityAssessment:
        with self._lock:
            ass = self._storage.get(assessment_id)
            if not ass:
                raise ReliabilityAssessmentNotFoundException(assessment_id)
            if ass.tenant_id != tenant_id:
                raise CrossTenantReliabilityIntelligenceException()
            return ass

    def get_latest_by_tenant(self, tenant_id: str) -> Optional[ReliabilityAssessment]:
        with self._lock:
            items = [a for a in self._storage.values() if a.tenant_id == tenant_id]
            if not items:
                return None
            return max(items, key=lambda x: x.created_at)


class SLORepository:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._storage: Dict[str, ServiceLevelObjective] = {}

    def save(self, slo: ServiceLevelObjective) -> ServiceLevelObjective:
        with self._lock:
            self._storage[slo.slo_id] = slo
            return slo

    def get_by_id(self, tenant_id: str, slo_id: str) -> ServiceLevelObjective:
        with self._lock:
            slo = self._storage.get(slo_id)
            if not slo:
                raise ReliabilityAssessmentNotFoundException(slo_id)
            if slo.tenant_id != tenant_id:
                raise CrossTenantReliabilityIntelligenceException()
            return slo


class FailurePredictionRepository:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._storage: Dict[str, FailurePrediction] = {}

    def save(self, pred: FailurePrediction) -> FailurePrediction:
        with self._lock:
            self._storage[pred.prediction_id] = pred
            return pred

    def get_by_id(self, tenant_id: str, pred_id: str) -> FailurePrediction:
        with self._lock:
            pred = self._storage.get(pred_id)
            if not pred:
                raise FailurePredictionNotFoundException(pred_id)
            if pred.tenant_id != tenant_id:
                raise CrossTenantReliabilityIntelligenceException()
            return pred

    def list_by_tenant(self, tenant_id: str) -> List[FailurePrediction]:
        with self._lock:
            return [p for p in self._storage.values() if p.tenant_id == tenant_id]


class ReliabilityEvidenceRepository:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._storage: Dict[str, ReliabilityEvidenceBundle] = {}

    def save(self, ev: ReliabilityEvidenceBundle) -> ReliabilityEvidenceBundle:
        with self._lock:
            self._storage[ev.evidence_id] = ev
            return ev

    def get_by_id(self, tenant_id: str, ev_id: str) -> ReliabilityEvidenceBundle:
        with self._lock:
            ev = self._storage.get(ev_id)
            if not ev:
                raise ReliabilityAssessmentNotFoundException(ev_id)
            if ev.tenant_id != tenant_id:
                raise CrossTenantReliabilityIntelligenceException()
            return ev
