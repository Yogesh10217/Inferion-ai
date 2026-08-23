"""Repository abstractions for Intelligence Platform."""

from typing import Dict, Any, Optional, List
from app.intelligence_platform.signals import IntelligenceSignal
from app.intelligence_platform.insights import Insight
from app.intelligence_platform.decisions import Decision
from app.intelligence_platform.recommendations import Recommendation


class PlatformIntelligenceRepository:
    """In-memory & persistence repository for intelligence artifacts."""

    def __init__(self) -> None:
        self._signals: Dict[str, IntelligenceSignal] = {}
        self._insights: Dict[str, Insight] = {}
        self._decisions: Dict[str, Decision] = {}
        self._recommendations: Dict[str, Recommendation] = {}

    def save_signal(self, signal: IntelligenceSignal) -> None:
        self._signals[signal.signal_id] = signal

    def get_signal(self, signal_id: str) -> Optional[IntelligenceSignal]:
        return self._signals.get(signal_id)

    def save_decision(self, decision: Decision) -> None:
        self._decisions[decision.decision_id] = decision

    def get_decision(self, decision_id: str) -> Optional[Decision]:
        return self._decisions.get(decision_id)

    def save_recommendation(self, recommendation: Recommendation) -> None:
        self._recommendations[recommendation.recommendation_id] = recommendation

    def get_recommendation(self, recommendation_id: str) -> Optional[Recommendation]:
        return self._recommendations.get(recommendation_id)
