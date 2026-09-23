"""Thread-safe, tenant-isolated repositories for Runtime Intelligence (Phase 5.57)."""

import threading
from typing import Any, Dict, List

from app.runtime_intelligence.exceptions import (
    CrossTenantRuntimeIntelligenceException,
    RuntimeAnomalyNotFoundException,
    RuntimeDriftNotFoundException,
    RuntimeHealthNotFoundException,
    RuntimeIntelligenceException,
    RuntimeRecommendationNotFoundException,
    RuntimeSignalNotFoundException,
)
from app.runtime_intelligence.models import (
    RuntimeAnomaly,
    RuntimeContext,
    RuntimeDrift,
    RuntimeEvidenceBundle,
    RuntimeHealthAssessment,
    RuntimeRecommendation,
    RuntimeSignal,
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


class RuntimeContextRepository:
    def __init__(self) -> None:
        self._storage: Dict[str, RuntimeContext] = {}
        self._lock = threading.RLock()

    def save(self, context: RuntimeContext) -> None:
        with self._lock:
            self._storage[context.context_id] = context

    def get_by_id(self, tenant_id: str, context_id: str) -> RuntimeContext:
        with self._lock:
            ctx = self._storage.get(context_id)
            if not ctx:
                raise RuntimeIntelligenceException("Runtime context not found")
            if ctx.tenant_id != tenant_id:
                raise CrossTenantRuntimeIntelligenceException()
            return ctx

    def get_by_tenant(self, tenant_id: str) -> List[RuntimeContext]:
        with self._lock:
            return [c for c in self._storage.values() if c.tenant_id == tenant_id]


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

    def get_by_tenant(self, tenant_id: str) -> List[RuntimeHealthAssessment]:
        with self._lock:
            return [h for h in self._storage.values() if h.tenant_id == tenant_id]


class RuntimeAnomalyRepository:
    def __init__(self) -> None:
        self._storage: Dict[str, RuntimeAnomaly] = {}
        self._lock = threading.RLock()

    def save(self, anomaly: RuntimeAnomaly) -> None:
        with self._lock:
            self._storage[anomaly.anomaly_id] = anomaly

    def get_by_id(self, tenant_id: str, anomaly_id: str) -> RuntimeAnomaly:
        with self._lock:
            anom = self._storage.get(anomaly_id)
            if not anom:
                raise RuntimeAnomalyNotFoundException(anomaly_id)
            if anom.tenant_id != tenant_id:
                raise CrossTenantRuntimeIntelligenceException()
            return anom

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

    def get_by_id(self, tenant_id: str, drift_id: str) -> RuntimeDrift:
        with self._lock:
            d = self._storage.get(drift_id)
            if not d:
                raise RuntimeDriftNotFoundException(drift_id)
            if d.tenant_id != tenant_id:
                raise CrossTenantRuntimeIntelligenceException()
            return d

    def get_by_tenant(self, tenant_id: str) -> List[RuntimeDrift]:
        with self._lock:
            return [d for d in self._storage.values() if d.tenant_id == tenant_id]


class RuntimeRiskRepository:
    def __init__(self) -> None:
        self._storage: Dict[str, Any] = {}
        self._lock = threading.RLock()

    def save(self, risk_assessment: Any) -> None:
        with self._lock:
            self._storage[risk_assessment.assessment_id] = risk_assessment

    def get_by_id(self, tenant_id: str, assessment_id: str) -> Any:
        with self._lock:
            r = self._storage.get(assessment_id)
            if not r:
                raise RuntimeIntelligenceException("Runtime risk assessment not found")
            if r.tenant_id != tenant_id:
                raise CrossTenantRuntimeIntelligenceException()
            return r

    def get_by_tenant(self, tenant_id: str) -> List[Any]:
        with self._lock:
            return [r for r in self._storage.values() if r.tenant_id == tenant_id]


class RuntimeDependencyRepository:
    def __init__(self) -> None:
        self._storage: Dict[str, Any] = {}
        self._lock = threading.RLock()

    def save(self, tenant_id: str, component_id: str, dependencies: List[str]) -> None:
        key = f"{tenant_id}:{component_id}"
        with self._lock:
            self._storage[key] = {
                "tenant_id": tenant_id,
                "component_id": component_id,
                "dependencies": dependencies,
            }

    def get_dependencies(self, tenant_id: str, component_id: str) -> List[str]:
        key = f"{tenant_id}:{component_id}"
        with self._lock:
            rec = self._storage.get(key)
            if not rec:
                return []
            if rec["tenant_id"] != tenant_id:
                raise CrossTenantRuntimeIntelligenceException()
            return rec["dependencies"]


class RuntimeRecommendationRepository:
    def __init__(self) -> None:
        self._storage: Dict[str, RuntimeRecommendation] = {}
        self._lock = threading.RLock()

    def save(self, recommendation: RuntimeRecommendation) -> None:
        with self._lock:
            self._storage[recommendation.recommendation_id] = recommendation

    def get_by_id(self, tenant_id: str, recommendation_id: str) -> RuntimeRecommendation:
        with self._lock:
            rec = self._storage.get(recommendation_id)
            if not rec:
                raise RuntimeRecommendationNotFoundException(recommendation_id)
            if rec.tenant_id != tenant_id:
                raise CrossTenantRuntimeIntelligenceException()
            return rec

    def get_by_tenant(self, tenant_id: str) -> List[RuntimeRecommendation]:
        with self._lock:
            return [r for r in self._storage.values() if r.tenant_id == tenant_id]


class RuntimeGovernanceRepository:
    def __init__(self) -> None:
        self._storage: Dict[str, Any] = {}
        self._lock = threading.RLock()

    def save(self, decision: Any) -> None:
        key = (
            decision.get("evaluation_id")
            if isinstance(decision, dict)
            else getattr(decision, "evaluation_id", None)
        ) or str(id(decision))
        with self._lock:
            self._storage[str(key)] = decision

    def get_by_id(self, tenant_id: str, evaluation_id: str) -> Any:
        with self._lock:
            dec = self._storage.get(evaluation_id)
            if not dec:
                raise RuntimeIntelligenceException("Governance evaluation not found")
            t_id = dec.get("tenant_id") if isinstance(dec, dict) else getattr(dec, "tenant_id", None)
            if t_id != tenant_id:
                raise CrossTenantRuntimeIntelligenceException()
            return dec

    def get_by_tenant(self, tenant_id: str) -> List[Any]:
        with self._lock:
            results = []
            for d in self._storage.values():
                t_id = d.get("tenant_id") if isinstance(d, dict) else getattr(d, "tenant_id", None)
                if t_id == tenant_id:
                    results.append(d)
            return results


class RuntimeDelegationRepository:
    def __init__(self) -> None:
        self._storage: Dict[str, Any] = {}
        self._lock = threading.RLock()

    def save(self, delegation: Any) -> None:
        del_id = (
            delegation.get("delegation_id")
            if isinstance(delegation, dict)
            else getattr(delegation, "delegation_id", None)
        ) or str(id(delegation))
        with self._lock:
            self._storage[str(del_id)] = delegation

    def get_by_id(self, tenant_id: str, delegation_id: str) -> Any:
        with self._lock:
            d = self._storage.get(delegation_id)
            if not d:
                raise RuntimeIntelligenceException("Delegation request not found")
            t_id = d.get("tenant_id") if isinstance(d, dict) else getattr(d, "tenant_id", None)
            if t_id != tenant_id:
                raise CrossTenantRuntimeIntelligenceException()
            return d

    def get_by_tenant(self, tenant_id: str) -> List[Any]:
        with self._lock:
            results = []
            for d in self._storage.values():
                t_id = d.get("tenant_id") if isinstance(d, dict) else getattr(d, "tenant_id", None)
                if t_id == tenant_id:
                    results.append(d)
            return results


class RuntimeVerificationRepository:
    def __init__(self) -> None:
        self._storage: Dict[str, Any] = {}
        self._lock = threading.RLock()

    def save(self, verification: Any) -> None:
        v_id = (
            verification.get("verification_id")
            if isinstance(verification, dict)
            else getattr(verification, "verification_id", None)
        ) or str(id(verification))
        with self._lock:
            self._storage[str(v_id)] = verification

    def get_by_id(self, tenant_id: str, verification_id: str) -> Any:
        with self._lock:
            v = self._storage.get(verification_id)
            if not v:
                raise RuntimeIntelligenceException("Runtime verification record not found")
            t_id = v.get("tenant_id") if isinstance(v, dict) else getattr(v, "tenant_id", None)
            if t_id != tenant_id:
                raise CrossTenantRuntimeIntelligenceException()
            return v

    def get_by_tenant(self, tenant_id: str) -> List[Any]:
        with self._lock:
            results = []
            for v in self._storage.values():
                t_id = v.get("tenant_id") if isinstance(v, dict) else getattr(v, "tenant_id", None)
                if t_id == tenant_id:
                    results.append(v)
            return results


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
                raise RuntimeIntelligenceException("Runtime evidence bundle not found")
            if ev.tenant_id != tenant_id:
                raise CrossTenantRuntimeIntelligenceException()
            return ev

    def get_by_tenant(self, tenant_id: str) -> List[RuntimeEvidenceBundle]:
        with self._lock:
            return [e for e in self._storage.values() if e.tenant_id == tenant_id]
