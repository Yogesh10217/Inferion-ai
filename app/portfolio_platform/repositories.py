"""Repository Abstractions for Portfolio Platform."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from app.portfolio_platform.strategy import EnterpriseStrategy
from app.portfolio_platform.initiatives import AIInitiative
from app.portfolio_platform.portfolio import Portfolio


class StrategyRepository(ABC):
    @abstractmethod
    def save(self, strategy: EnterpriseStrategy) -> EnterpriseStrategy:
        pass

    @abstractmethod
    def get_by_id(self, strategy_id: str, tenant_id: str) -> Optional[EnterpriseStrategy]:
        pass

    @abstractmethod
    def list(self, tenant_id: str) -> List[EnterpriseStrategy]:
        pass


class InMemoryStrategyRepository(StrategyRepository):
    def __init__(self) -> None:
        self._store: Dict[str, EnterpriseStrategy] = {}

    def save(self, strategy: EnterpriseStrategy) -> EnterpriseStrategy:
        self._store[strategy.strategy_id] = strategy
        return strategy

    def get_by_id(self, strategy_id: str, tenant_id: str) -> Optional[EnterpriseStrategy]:
        strat = self._store.get(strategy_id)
        if strat and (strat.tenant_id == tenant_id or tenant_id == "global"):
            return strat
        return None

    def list(self, tenant_id: str) -> List[EnterpriseStrategy]:
        return [s for s in self._store.values() if s.tenant_id in (tenant_id, "global")]


class PortfolioRepository:
    """Production Repository Coordinator."""

    def __init__(self, use_memory: bool = True) -> None:
        self.use_memory = use_memory
        self.strategy_repo: StrategyRepository = InMemoryStrategyRepository()
