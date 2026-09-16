"""Repository Abstractions for Decision Intelligence Platform."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from app.decision_intelligence.decisions import EnterpriseDecision


class DecisionRepository(ABC):
    @abstractmethod
    def save(self, decision: EnterpriseDecision) -> EnterpriseDecision:
        pass

    @abstractmethod
    def get_by_id(self, decision_id: str, tenant_id: str) -> Optional[EnterpriseDecision]:
        pass

    @abstractmethod
    def list(self, tenant_id: str) -> List[EnterpriseDecision]:
        pass


class InMemoryDecisionRepository(DecisionRepository):
    def __init__(self) -> None:
        self._store: Dict[str, EnterpriseDecision] = {}

    def save(self, decision: EnterpriseDecision) -> EnterpriseDecision:
        self._store[decision.decision_id] = decision
        return decision

    def get_by_id(self, decision_id: str, tenant_id: str) -> Optional[EnterpriseDecision]:
        dec = self._store.get(decision_id)
        if dec and (dec.tenant_id == tenant_id or tenant_id == "global"):
            return dec
        return None

    def list(self, tenant_id: str) -> List[EnterpriseDecision]:
        return [d for d in self._store.values() if d.tenant_id in (tenant_id, "global")]
