"""Thread-safe, tenant-isolated repositories for Runtime Intelligence (Phase 5.54)."""

import threading
from typing import Dict, List, Optional
from app.runtime_intelligence.models import (
    RuntimeSignal,
    RuntimeHealthAssessment,
    RuntimeAnomaly,
    RuntimeDrift,
    RuntimeRecommendation,
    RuntimeEvidenceBundle,
)
from app.runtime_intelligence.exceptions import (
    CrossTenantRuntimeIntelligenceException,
    RuntimeSignalNotFoundException,
    RuntimeHealthNotFoundException,
    RuntimeAnomalyNotFoundException,
    RuntimeDriftNotFoundException,
    RuntimeRecommendationNotFoundException,
)


class RuntimeSignalRepository:
    def __init__(self) -> None:
        self._storage: Dict[str, RuntimeSignal] = {}
        self._lock = threading.RLock()

    def save(self, signal: RuntimeSignal) -> None:
        with self._lock:
            self._storage[signal.signal_id] = signal

    def get_by_id(self, tenant_id: str, signal_id: str) -> RuntimeSignal:
        with self._lock:
            sig = self._storage.get(signal_id)
            if not sig:
                raise RuntimeSignalNotFoundException(signal_id)
            if sig.tenant_id != tenant_id:
                raise CrossTenantRuntimeIntelligenceException()
            return sig

    def get_by_tenant(self, tenant_id: str) -> List[RuntimeSignal]:
        with self._lock:
            return [s for s in self._storage.values() if s.tenant_id == tenant_id]


class RuntimeHealthRepository:
    def __init__(self) -> None:
        self._storage: Dict[str, RuntimeHealthAssessment] = {}
        self._lock = threading.RLock()

    def save(self, assessment: RuntimeHealthAssessment) -> None:
        with self._lock:
            self._storage[assessment.assessment_id] = assessment

    def get_by_id(self, tenant_id: str, assessment_id: str) -> RuntimeHealthAssessment:
        with self._lock:
            rh = self._storage.get(assessment_id)
            if not rh:
                raise RuntimeHealthNotFoundException(assessment_id)
            if rh.tenant_id != tenant_id:
                raise CrossTenantRuntimeIntelligenceException()
            return rh


class RuntimeAnomalyRepository:
    def __init__(self) -> None:
        self._storage: Dict[str, RuntimeAnomaly] = {}
        self._lock = threading.RLock()

    def save(self, anomaly: RuntimeAnomaly) -> None:
        with self._lock:
            self._storage[anomaly.anomaly_id] = anomaly

    def get_by_tenant(self, tenant_id: str) -> List[RuntimeAnomaly]:
        with self._lock:
            return [a for a in self._storage.values() if a.tenant_id == tenant_id]


class RuntimeDriftRepository:
    def __init__(self) -> None:
        self._storage: Dict[str, RuntimeDrift] = {}
        self._lock = threading.RLock()

    def save(self, drift: RuntimeDrift) -> None:
        with self._lock:
            self._storage[drift.drift_id] = drift

    def get_by_tenant(self, tenant_id: str) -> List[RuntimeDrift]:
        with self._lock:
            return [d for d in self._storage.values() if d.tenant_id == tenant_id]


class RuntimeRecommendationRepository:
    def __init__(self) -> None:
        self._storage: Dict[str, RuntimeRecommendation] = {}
        self._lock = threading.RLock()

    def save(self, recommendation: RuntimeRecommendation) -> None:
        with self._lock:
            self._storage[recommendation.recommendation_id] = recommendation

    def get_by_tenant(self, tenant_id: str) -> List[RuntimeRecommendation]:
        with self._lock:
            return [r for r in self._storage.values() if r.tenant_id == tenant_id]


class RuntimeEvidenceRepository:
    def __init__(self) -> None:
        self._storage: Dict[str, RuntimeEvidenceBundle] = {}
        self._lock = threading.RLock()

    def save(self, evidence: RuntimeEvidenceBundle) -> None:
        with self._lock:
            self._storage[evidence.evidence_id] = evidence

    def get_by_id(self, tenant_id: str, evidence_id: str) -> RuntimeEvidenceBundle:
        with self._lock:
            ev = self._storage.get(evidence_id)
            if not ev:
                raise RuntimeIntelligenceException(f"Runtime evidence bundle '{evidence_id}' not found")
            if ev.tenant_id != tenant_id:
                raise CrossTenantRuntimeIntelligenceException()
            return ev
