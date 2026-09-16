"""Thread-safe tenant-isolated repositories for Continuous Assurance (Phase 5.54)."""

import threading
from typing import Dict, List, Optional

from app.continuous_assurance.exceptions import (
    AssuranceDriftNotFoundException,
    ContinuousAssuranceRecordNotFoundException,
    ControlEffectivenessNotFoundException,
    CrossTenantContinuousAssuranceException,
    RuntimeObservationNotFoundException,
)
from app.continuous_assurance.models import (
    AdaptiveControlRecommendation,
    AssuranceDrift,
    ContinuousAssuranceAssessment,
    ContinuousAssuranceEvidenceBundle,
    ContinuousAssuranceSnapshot,
    ContinuousVerificationResult,
    ControlEffectivenessAssessment,
    RuntimeObservation,
)


class RuntimeObservationRepository:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._storage: Dict[str, RuntimeObservation] = {}

    def save(self, obs: RuntimeObservation) -> RuntimeObservation:
        with self._lock:
            self._storage[obs.observation_id] = obs
            return obs

    def get_by_id(self, tenant_id: str, obs_id: str) -> RuntimeObservation:
        with self._lock:
            obs = self._storage.get(obs_id)
            if not obs:
                raise RuntimeObservationNotFoundException(obs_id)
            if obs.tenant_id != tenant_id:
                raise CrossTenantContinuousAssuranceException()
            return obs

    def list_by_tenant(self, tenant_id: str) -> List[RuntimeObservation]:
        with self._lock:
            return [o for o in self._storage.values() if o.tenant_id == tenant_id]


class ContinuousAssuranceRepository:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._storage: Dict[str, ContinuousAssuranceAssessment] = {}

    def save(self, assessment: ContinuousAssuranceAssessment) -> ContinuousAssuranceAssessment:
        with self._lock:
            self._storage[assessment.assessment_id] = assessment
            return assessment

    def get_by_id(self, tenant_id: str, assessment_id: str) -> ContinuousAssuranceAssessment:
        with self._lock:
            ass = self._storage.get(assessment_id)
            if not ass:
                raise ContinuousAssuranceRecordNotFoundException(assessment_id)
            if ass.tenant_id != tenant_id:
                raise CrossTenantContinuousAssuranceException()
            return ass

    def get_latest_by_tenant(self, tenant_id: str) -> Optional[ContinuousAssuranceAssessment]:
        with self._lock:
            items = [a for a in self._storage.values() if a.tenant_id == tenant_id]
            if not items:
                return None
            return max(items, key=lambda x: x.created_at)


class ControlEffectivenessRepository:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._storage: Dict[str, ControlEffectivenessAssessment] = {}

    def save(self, assessment: ControlEffectivenessAssessment) -> ControlEffectivenessAssessment:
        with self._lock:
            self._storage[assessment.assessment_id] = assessment
            return assessment

    def get_by_id(self, tenant_id: str, assessment_id: str) -> ControlEffectivenessAssessment:
        with self._lock:
            ctrl = self._storage.get(assessment_id)
            if not ctrl:
                raise ControlEffectivenessNotFoundException(assessment_id)
            if ctrl.tenant_id != tenant_id:
                raise CrossTenantContinuousAssuranceException()
            return ctrl

    def list_by_tenant(self, tenant_id: str) -> List[ControlEffectivenessAssessment]:
        with self._lock:
            return [c for c in self._storage.values() if c.tenant_id == tenant_id]


class DriftRepository:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._storage: Dict[str, AssuranceDrift] = {}

    def save(self, drift: AssuranceDrift) -> AssuranceDrift:
        with self._lock:
            self._storage[drift.drift_id] = drift
            return drift

    def get_by_id(self, tenant_id: str, drift_id: str) -> AssuranceDrift:
        with self._lock:
            drift = self._storage.get(drift_id)
            if not drift:
                raise AssuranceDriftNotFoundException(drift_id)
            if drift.tenant_id != tenant_id:
                raise CrossTenantContinuousAssuranceException()
            return drift

    def list_by_tenant(self, tenant_id: str) -> List[AssuranceDrift]:
        with self._lock:
            return [d for d in self._storage.values() if d.tenant_id == tenant_id]


class VerificationRepository:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._storage: Dict[str, ContinuousVerificationResult] = {}

    def save(self, ver: ContinuousVerificationResult) -> ContinuousVerificationResult:
        with self._lock:
            self._storage[ver.verification_id] = ver
            return ver

    def get_by_id(self, tenant_id: str, ver_id: str) -> ContinuousVerificationResult:
        with self._lock:
            ver = self._storage.get(ver_id)
            if not ver:
                raise ContinuousAssuranceRecordNotFoundException(ver_id)
            if ver.tenant_id != tenant_id:
                raise CrossTenantContinuousAssuranceException()
            return ver

    def list_by_tenant(self, tenant_id: str) -> List[ContinuousVerificationResult]:
        with self._lock:
            return [v for v in self._storage.values() if v.tenant_id == tenant_id]


class RecommendationRepository:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._storage: Dict[str, AdaptiveControlRecommendation] = {}

    def save(self, rec: AdaptiveControlRecommendation) -> AdaptiveControlRecommendation:
        with self._lock:
            self._storage[rec.recommendation_id] = rec
            return rec

    def list_by_tenant(self, tenant_id: str) -> List[AdaptiveControlRecommendation]:
        with self._lock:
            return [r for r in self._storage.values() if r.tenant_id == tenant_id]


class EvidenceRepository:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._storage: Dict[str, ContinuousAssuranceEvidenceBundle] = {}

    def save(self, ev: ContinuousAssuranceEvidenceBundle) -> ContinuousAssuranceEvidenceBundle:
        with self._lock:
            self._storage[ev.evidence_id] = ev
            return ev

    def get_by_id(self, tenant_id: str, ev_id: str) -> ContinuousAssuranceEvidenceBundle:
        with self._lock:
            ev = self._storage.get(ev_id)
            if not ev:
                raise ContinuousAssuranceRecordNotFoundException(ev_id)
            if ev.tenant_id != tenant_id:
                raise CrossTenantContinuousAssuranceException()
            return ev


class SnapshotRepository:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._storage: Dict[str, ContinuousAssuranceSnapshot] = {}

    def save(self, snap: ContinuousAssuranceSnapshot) -> ContinuousAssuranceSnapshot:
        with self._lock:
            self._storage[snap.snapshot_id] = snap
            return snap

    def get_by_id(self, tenant_id: str, snap_id: str) -> ContinuousAssuranceSnapshot:
        with self._lock:
            snap = self._storage.get(snap_id)
            if not snap:
                raise ContinuousAssuranceRecordNotFoundException(snap_id)
            if snap.tenant_id != tenant_id:
                raise CrossTenantContinuousAssuranceException()
            return snap
