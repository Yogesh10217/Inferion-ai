"""Thread-safe, tenant-isolated repositories for Capacity Intelligence (Phase 5.56)."""

import threading
from typing import Dict, List, Optional
from app.capacity_intelligence.models import (
    ResourceProfile,
    CapacityTelemetry,
    CapacityAssessment,
    CapacityForecast,
    Bottleneck,
    CapacityRecommendation,
    CapacityEvidenceBundle,
)
from app.capacity_intelligence.exceptions import (
    CrossTenantCapacityIntelligenceException,
    ResourceProfileNotFoundException,
    CapacityAssessmentNotFoundException,
    CapacityForecastNotFoundException,
    BottleneckNotFoundException,
    CapacityRecommendationNotFoundException,
    CapacityIntelligenceException,
)


class ResourceRepository:
    def __init__(self) -> None:
        self._storage: Dict[str, ResourceProfile] = {}
        self._lock = threading.RLock()

    def save(self, profile: ResourceProfile) -> None:
        with self._lock:
            self._storage[profile.profile_id] = profile

    def get_by_id(self, tenant_id: str, profile_id: str) -> ResourceProfile:
        with self._lock:
            prof = self._storage.get(profile_id)
            if not prof:
                raise ResourceProfileNotFoundException(profile_id)
            if prof.tenant_id != tenant_id:
                raise CrossTenantCapacityIntelligenceException()
            return prof


class TelemetryRepository:
    def __init__(self) -> None:
        self._storage: Dict[str, CapacityTelemetry] = {}
        self._lock = threading.RLock()

    def save(self, telemetry: CapacityTelemetry) -> None:
        with self._lock:
            self._storage[telemetry.telemetry_id] = telemetry

    def get_by_tenant(self, tenant_id: str) -> List[CapacityTelemetry]:
        with self._lock:
            return [t for t in self._storage.values() if t.tenant_id == tenant_id]


class CapacityAssessmentRepository:
    def __init__(self) -> None:
        self._storage: Dict[str, CapacityAssessment] = {}
        self._lock = threading.RLock()

    def save(self, assessment: CapacityAssessment) -> None:
        with self._lock:
            self._storage[assessment.assessment_id] = assessment

    def get_by_id(self, tenant_id: str, assessment_id: str) -> CapacityAssessment:
        with self._lock:
            ass = self._storage.get(assessment_id)
            if not ass:
                raise CapacityAssessmentNotFoundException(assessment_id)
            if ass.tenant_id != tenant_id:
                raise CrossTenantCapacityIntelligenceException()
            return ass


class ForecastRepository:
    def __init__(self) -> None:
        self._storage: Dict[str, CapacityForecast] = {}
        self._lock = threading.RLock()

    def save(self, forecast: CapacityForecast) -> None:
        with self._lock:
            self._storage[forecast.forecast_id] = forecast

    def get_by_id(self, tenant_id: str, forecast_id: str) -> CapacityForecast:
        with self._lock:
            f = self._storage.get(forecast_id)
            if not f:
                raise CapacityForecastNotFoundException(forecast_id)
            if f.tenant_id != tenant_id:
                raise CrossTenantCapacityIntelligenceException()
            return f


class BottleneckRepository:
    def __init__(self) -> None:
        self._storage: Dict[str, Bottleneck] = {}
        self._lock = threading.RLock()

    def save(self, bottleneck: Bottleneck) -> None:
        with self._lock:
            self._storage[bottleneck.bottleneck_id] = bottleneck

    def get_by_tenant(self, tenant_id: str) -> List[Bottleneck]:
        with self._lock:
            return [b for b in self._storage.values() if b.tenant_id == tenant_id]


class RecommendationRepository:
    def __init__(self) -> None:
        self._storage: Dict[str, CapacityRecommendation] = {}
        self._lock = threading.RLock()

    def save(self, recommendation: CapacityRecommendation) -> None:
        with self._lock:
            self._storage[recommendation.recommendation_id] = recommendation

    def get_by_tenant(self, tenant_id: str) -> List[CapacityRecommendation]:
        with self._lock:
            return [r for r in self._storage.values() if r.tenant_id == tenant_id]


class EvidenceRepository:
    def __init__(self) -> None:
        self._storage: Dict[str, CapacityEvidenceBundle] = {}
        self._lock = threading.RLock()

    def save(self, evidence: CapacityEvidenceBundle) -> None:
        with self._lock:
            self._storage[evidence.evidence_id] = evidence

    def get_by_id(self, tenant_id: str, evidence_id: str) -> CapacityEvidenceBundle:
        with self._lock:
            ev = self._storage.get(evidence_id)
            if not ev:
                raise CapacityIntelligenceException(f"Capacity evidence bundle '{evidence_id}' not found")
            if ev.tenant_id != tenant_id:
                raise CrossTenantCapacityIntelligenceException()
            return ev


CapacityTelemetryRepository = TelemetryRepository
CapacityForecastRepository = ForecastRepository
CapacityRecommendationRepository = RecommendationRepository
CapacityEvidenceRepository = EvidenceRepository
