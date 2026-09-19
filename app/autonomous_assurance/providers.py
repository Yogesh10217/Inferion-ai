"""
Autonomous Assurance Provider Interface & Provider Registry (Decoupled Architecture).
Decouples AutonomousAssuranceManager from direct domain manager imports.
"""

import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

logger = logging.getLogger(__name__)


class AssuranceDomain(str, Enum):
    SECURITY = "security"
    IDENTITY = "identity"
    OPERATIONS = "operations"
    UNIFIED = "unified"
    DECISION = "decision"
    POLICY = "policy"
    KNOWLEDGE = "knowledge"
    CONTROL = "control"


@runtime_checkable
class AutonomousAssuranceProvider(Protocol):
    """Protocol interface that domain managers implement or wrap to supply intelligence outputs."""

    def get_domain(self) -> AssuranceDomain: ...

    def get_signals(self, tenant_id: str) -> List[Dict[str, Any]]: ...

    def get_findings(self, tenant_id: str) -> List[Dict[str, Any]]: ...

    def get_risks(self, tenant_id: str) -> List[Dict[str, Any]]: ...

    def get_recommendations(self, tenant_id: str) -> List[Dict[str, Any]]: ...

    def get_assurance(self, tenant_id: str) -> Dict[str, Any]: ...

    def get_trust(self, tenant_id: str) -> Dict[str, Any]: ...

    def get_snapshots(self, tenant_id: str) -> Optional[Dict[str, Any]]: ...


class BaseAutonomousAssuranceProvider(ABC):
    """Abstract base class for autonomous assurance providers."""

    @abstractmethod
    def get_domain(self) -> AssuranceDomain:
        pass

    @abstractmethod
    def get_signals(self, tenant_id: str) -> List[Dict[str, Any]]:
        pass

    def get_findings(self, tenant_id: str) -> List[Dict[str, Any]]:
        return []

    def get_risks(self, tenant_id: str) -> List[Dict[str, Any]]:
        return []

    def get_recommendations(self, tenant_id: str) -> List[Dict[str, Any]]:
        return []

    def get_assurance(self, tenant_id: str) -> Dict[str, Any]:
        return {"domain": self.get_domain().value, "score": 90.0, "status": "HEALTHY"}

    def get_trust(self, tenant_id: str) -> Dict[str, Any]:
        return {"domain": self.get_domain().value, "trust_score": 90.0}

    def get_snapshots(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        return None


class MockAutonomousAssuranceProvider(BaseAutonomousAssuranceProvider):
    """Mock provider for unit testing provider integration."""

    def __init__(
        self, provider_name: str = "operations_assurance", domain: AssuranceDomain = AssuranceDomain.OPERATIONS
    ) -> None:
        self.provider_name = provider_name
        self.domain = domain

    def get_domain(self) -> AssuranceDomain:
        return self.domain

    def get_signals(self, tenant_id: str) -> List[Dict[str, Any]]:
        return [{"signal_id": "sig_mock", "status": "HEALTHY"}]

    def validate_action(self, action_name: str, parameters: Dict[str, Any]) -> bool:
        return True


class AutonomousAssuranceProviderRegistry:
    """Registry maintaining active domain intelligence providers without importing concrete managers."""

    def __init__(self) -> None:
        self._providers: Dict[str, Any] = {}

    def register_provider(self, domain: Any, provider: Any) -> None:
        key = domain.value if isinstance(domain, AssuranceDomain) else str(domain)
        self._providers[key] = provider
        logger.info(f"[ASSURANCE PROVIDER REGISTRY] Registered provider for domain '{key}'")

    def unregister_provider(self, domain: Any) -> None:
        key = domain.value if isinstance(domain, AssuranceDomain) else str(domain)
        if key in self._providers:
            del self._providers[key]

    def get_provider(self, domain: Any) -> Optional[Any]:
        key = domain.value if isinstance(domain, AssuranceDomain) else str(domain)
        return self._providers.get(key)

    def list_providers(self) -> Dict[str, Any]:
        return dict(self._providers)
