"""Thread-Safe, Tenant-Isolated Repositories for Phase 5.58."""

import threading
from typing import Dict, Any, List, Optional

from app.platform_integration.models import (
    CrossPhaseSignal,
    CrossPhaseFinding,
    CrossPhaseAssessment,
    CrossPhaseCorrelation,
    CrossPhaseRecommendation,
)
from app.platform_integration.context.builder import PlatformIntegrationContext
from app.platform_integration.investigation.engine import CrossPhaseInvestigationResult
from app.platform_integration.exceptions import CrossTenantPlatformIntegrationException


class IntegrationContextRepository:
    """Thread-safe, tenant-isolated repository for PlatformIntegrationContext."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._contexts: Dict[str, Dict[str, PlatformIntegrationContext]] = {}

    def save(self, context: PlatformIntegrationContext) -> PlatformIntegrationContext:
        with self._lock:
            tenant_store = self._contexts.setdefault(context.tenant_id, {})
            tenant_store[context.context_id] = context
            return context

    def get(self, tenant_id: str, context_id: str) -> Optional[PlatformIntegrationContext]:
        with self._lock:
            # Check for cross-tenant access attempt
            for tid, store in self._contexts.items():
                if context_id in store and tid != tenant_id:
                    raise CrossTenantPlatformIntegrationException("Access denied")
            return self._contexts.get(tenant_id, {}).get(context_id)

    def list_by_tenant(self, tenant_id: str) -> List[PlatformIntegrationContext]:
        with self._lock:
            return list(self._contexts.get(tenant_id, {}).values())


class CorrelationRepository:
    """Thread-safe, tenant-isolated repository for CrossPhaseCorrelation."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._correlations: Dict[str, Dict[str, CrossPhaseCorrelation]] = {}

    def save(self, correlation: CrossPhaseCorrelation) -> CrossPhaseCorrelation:
        with self._lock:
            tenant_store = self._correlations.setdefault(correlation.tenant_id, {})
            tenant_store[correlation.correlation_id] = correlation
            return correlation

    def get(self, tenant_id: str, correlation_id: str) -> Optional[CrossPhaseCorrelation]:
        with self._lock:
            for tid, store in self._correlations.items():
                if correlation_id in store and tid != tenant_id:
                    raise CrossTenantPlatformIntegrationException("Access denied")
            return self._correlations.get(tenant_id, {}).get(correlation_id)

    def list_by_tenant(self, tenant_id: str) -> List[CrossPhaseCorrelation]:
        with self._lock:
            return list(self._correlations.get(tenant_id, {}).values())


class InvestigationRepository:
    """Thread-safe, tenant-isolated repository for CrossPhaseInvestigationResult."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._investigations: Dict[str, Dict[str, CrossPhaseInvestigationResult]] = {}

    def save(self, inv: CrossPhaseInvestigationResult) -> CrossPhaseInvestigationResult:
        with self._lock:
            tenant_store = self._investigations.setdefault(inv.tenant_id, {})
            tenant_store[inv.investigation_id] = inv
            return inv

    def get(self, tenant_id: str, investigation_id: str) -> Optional[CrossPhaseInvestigationResult]:
        with self._lock:
            for tid, store in self._investigations.items():
                if investigation_id in store and tid != tenant_id:
                    raise CrossTenantPlatformIntegrationException("Access denied")
            return self._investigations.get(tenant_id, {}).get(investigation_id)


class RecommendationRepository:
    """Thread-safe, tenant-isolated repository for CrossPhaseRecommendation."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._recs: Dict[str, Dict[str, CrossPhaseRecommendation]] = {}

    def save(self, rec: CrossPhaseRecommendation) -> CrossPhaseRecommendation:
        with self._lock:
            tenant_store = self._recs.setdefault(rec.tenant_id, {})
            tenant_store[rec.recommendation_id] = rec
            return rec

    def get(self, tenant_id: str, recommendation_id: str) -> Optional[CrossPhaseRecommendation]:
        with self._lock:
            for tid, store in self._recs.items():
                if recommendation_id in store and tid != tenant_id:
                    raise CrossTenantPlatformIntegrationException("Access denied")
            return self._recs.get(tenant_id, {}).get(recommendation_id)

    def list_by_tenant(self, tenant_id: str) -> List[CrossPhaseRecommendation]:
        with self._lock:
            return list(self._recs.get(tenant_id, {}).values())
