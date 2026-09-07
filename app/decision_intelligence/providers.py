"""
Decision Intelligence Provider Interface & Provider Registry (Decoupled Architecture).
Decouples DecisionIntelligenceManager from direct domain manager imports.
"""

import logging
from typing import Dict, Any, List, Optional, Protocol, runtime_checkable
from datetime import datetime, timezone
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class IntelligenceDomain(str, Enum):
    SECURITY = "security"
    IDENTITY = "identity"
    OPERATIONS = "operations"
    UNIFIED = "unified"
    POLICY = "policy"
    KNOWLEDGE = "knowledge"
    DATA = "data"
    MODEL = "model"


@runtime_checkable
class DecisionIntelligenceProvider(Protocol):
    """Protocol interface that domain managers implement or wrap to supply intelligence context to DecisionIntelligence."""

    def get_domain(self) -> IntelligenceDomain:
        ...

    def get_domain_context(self, tenant_id: str) -> Dict[str, Any]:
        ...

    def get_domain_signals(self, tenant_id: str) -> List[Dict[str, Any]]:
        ...

    def get_domain_policy_evaluations(self, tenant_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        ...


class BaseDecisionIntelligenceProvider(ABC):
    """Abstract base class for decision intelligence providers."""

    @abstractmethod
    def get_domain(self) -> IntelligenceDomain:
        pass

    @abstractmethod
    def get_domain_context(self, tenant_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_domain_signals(self, tenant_id: str) -> List[Dict[str, Any]]:
        pass

    def get_domain_policy_evaluations(self, tenant_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"domain": self.get_domain().value, "status": "EVALUATED", "passed": True}


class DecisionIntelligenceProviderRegistry:
    """Registry maintaining active decision intelligence providers without importing concrete manager implementations."""

    def __init__(self) -> None:
        self._providers: Dict[IntelligenceDomain, Any] = {}

    def register_provider(self, domain: IntelligenceDomain, provider: Any) -> None:
        self._providers[domain] = provider
        logger.info(f"[DECISION PROVIDER REGISTRY] Registered provider for domain '{domain.value}'")

    def unregister_provider(self, domain: IntelligenceDomain) -> None:
        if domain in self._providers:
            del self._providers[domain]

    def get_provider(self, domain: IntelligenceDomain) -> Optional[Any]:
        return self._providers.get(domain)

    def list_providers(self) -> Dict[IntelligenceDomain, Any]:
        return dict(self._providers)


# Alias
ProviderRegistry = DecisionIntelligenceProviderRegistry
