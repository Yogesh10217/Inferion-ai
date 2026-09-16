"""Domain Intelligence Provider Interface & Provider Registry (Decoupled Architecture)."""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from app.unified_intelligence.domains import DomainHealth, IntelligenceDomain

logger = logging.getLogger(__name__)


@runtime_checkable
class IntelligenceProvider(Protocol):
    """Protocol interface that domain managers implement or wrap to supply intelligence outputs to UnifiedIntelligence."""

    def get_domain(self) -> IntelligenceDomain:
        ...

    def get_signals(self, tenant_id: str) -> List[Dict[str, Any]]:
        """Fetch raw domain signals."""
        ...

    def get_assurance(self, tenant_id: str) -> Dict[str, Any]:
        """Fetch domain assurance status or score."""
        ...

    def get_snapshot(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Fetch domain point-in-time snapshot."""
        ...


class BaseIntelligenceProvider(ABC):
    """Abstract base class for domain intelligence providers."""

    @abstractmethod
    def get_domain(self) -> IntelligenceDomain:
        pass

    @abstractmethod
    def get_signals(self, tenant_id: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_assurance(self, tenant_id: str) -> Dict[str, Any]:
        pass

    def get_snapshot(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        return None


class ProviderRegistry:
    """Registry maintaining active domain intelligence providers without importing concrete manager implementations."""

    def __init__(self) -> None:
        self._providers: Dict[IntelligenceDomain, Any] = {}

    def register_provider(self, domain: IntelligenceDomain, provider: Any) -> None:
        self._providers[domain] = provider
        logger.info(f"[PROVIDER REGISTRY] Registered intelligence provider for domain '{domain.value}'")

    def unregister_provider(self, domain: IntelligenceDomain) -> None:
        if domain in self._providers:
            del self._providers[domain]

    def get_provider(self, domain: IntelligenceDomain) -> Optional[Any]:
        return self._providers.get(domain)

    def list_providers(self) -> Dict[IntelligenceDomain, Any]:
        return dict(self._providers)

    def get_domain_health(self, domain: IntelligenceDomain) -> DomainHealth:
        provider = self.get_provider(domain)
        if not provider:
            return DomainHealth(domain=domain, status="UNREACHABLE")
        return DomainHealth(domain=domain, status="HEALTHY", last_signal_timestamp=datetime.now(timezone.utc))


# Alias for backward compatibility / explicit naming
IntelligenceProviderRegistry = ProviderRegistry
