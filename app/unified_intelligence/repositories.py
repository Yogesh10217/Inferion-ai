"""
Data Access Repositories for Phase 5.51 Enterprise AI Unified Intelligence.

Provides in-memory and database persistence repositories with strict tenant isolation.
"""

from typing import List, Dict, Optional

from app.unified_intelligence.exceptions import (
    CrossTenantUnifiedIntelligenceException,
    InvalidUnifiedIntelligenceInputException
)
from app.unified_intelligence.signals import UnifiedSignal
from app.unified_intelligence.situation_awareness import EnterpriseSituation
from app.unified_intelligence.recommendations import UnifiedRecommendation
from app.unified_intelligence.investigations import UnifiedInvestigation


class UnifiedIntelligenceRepository:
    """
    Repository for Unified Intelligence state entities with strict tenant filtering.
    """
    def __init__(self):
        self._signals: Dict[str, UnifiedSignal] = {}
        self._situations: Dict[str, EnterpriseSituation] = {}
        self._recommendations: Dict[str, UnifiedRecommendation] = {}
        self._investigations: Dict[str, UnifiedInvestigation] = {}

    def save_signal(self, tenant_id: str, signal: UnifiedSignal) -> None:
        if signal.tenant_id != tenant_id:
            raise CrossTenantUnifiedIntelligenceException(
                f"Tenant mismatch saving signal: requested {tenant_id}, signal has {signal.tenant_id}"
            )
        self._signals[signal.signal_id] = signal

    def get_signal(self, tenant_id: str, signal_id: str) -> Optional[UnifiedSignal]:
        sig = self._signals.get(signal_id)
        if not sig:
            return None
        if sig.tenant_id != tenant_id:
            raise CrossTenantUnifiedIntelligenceException(
                f"Tenant mismatch getting signal: requested {tenant_id}, signal has {sig.tenant_id}"
            )
        return sig

    def list_signals(self, tenant_id: str) -> List[UnifiedSignal]:
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")
        return [s for s in self._signals.values() if s.tenant_id == tenant_id]

    def save_situation(self, tenant_id: str, situation: EnterpriseSituation) -> None:
        if situation.tenant_id != tenant_id:
            raise CrossTenantUnifiedIntelligenceException(
                f"Tenant mismatch saving situation: requested {tenant_id}, situation has {situation.tenant_id}"
            )
        self._situations[situation.situation_id] = situation

    def get_situation(self, tenant_id: str, situation_id: str) -> Optional[EnterpriseSituation]:
        sit = self._situations.get(situation_id)
        if not sit:
            return None
        if sit.tenant_id != tenant_id:
            raise CrossTenantUnifiedIntelligenceException(
                f"Tenant mismatch getting situation: requested {tenant_id}, situation has {sit.tenant_id}"
            )
        return sit

    def list_situations(self, tenant_id: str) -> List[EnterpriseSituation]:
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")
        return [s for s in self._situations.values() if s.tenant_id == tenant_id]

    def save_recommendation(self, tenant_id: str, recommendation: UnifiedRecommendation) -> None:
        if recommendation.tenant_id != tenant_id:
            raise CrossTenantUnifiedIntelligenceException(
                f"Tenant mismatch saving recommendation: requested {tenant_id}, recommendation has {recommendation.tenant_id}"
            )
        self._recommendations[recommendation.recommendation_id] = recommendation

    def list_recommendations(self, tenant_id: str) -> List[UnifiedRecommendation]:
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")
        return [r for r in self._recommendations.values() if r.tenant_id == tenant_id]

    def save_investigation(self, tenant_id: str, investigation: UnifiedInvestigation) -> None:
        if investigation.tenant_id != tenant_id:
            raise CrossTenantUnifiedIntelligenceException(
                f"Tenant mismatch saving investigation: requested {tenant_id}, investigation has {investigation.tenant_id}"
            )
        self._investigations[investigation.investigation_id] = investigation

    def list_investigations(self, tenant_id: str) -> List[UnifiedInvestigation]:
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")
        return [inv for inv in self._investigations.values() if inv.tenant_id == tenant_id]
