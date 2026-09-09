"""Provider-decoupled architecture for Reliability Intelligence (Phase 5.55)."""

import logging
from typing import Dict, Any, Optional, Protocol, List, Union, runtime_checkable
from enum import Enum

logger = logging.getLogger(__name__)


@runtime_checkable
class ReliabilityIntelligenceProvider(Protocol):
    """Protocol for cross-domain reliability intelligence providers."""

    def get_provider_name(self) -> str:
        ...

    def get_domain(self) -> str:
        ...

    def collect_signals(self, tenant_id: str) -> List[Dict[str, Any]]:
        ...

    def collect_health(self, tenant_id: str) -> Dict[str, Any]:
        ...

    def collect_metrics(self, tenant_id: str) -> Dict[str, Any]:
        ...

    def collect_failures(self, tenant_id: str) -> List[Dict[str, Any]]:
        ...

    def collect_incidents(self, tenant_id: str) -> List[Dict[str, Any]]:
        ...

    def collect_dependencies(self, tenant_id: str) -> List[Dict[str, Any]]:
        ...

    def collect_risk(self, tenant_id: str) -> Dict[str, Any]:
        ...

    def collect_assurance(self, tenant_id: str) -> float:
        ...

    def collect_trust(self, tenant_id: str) -> Dict[str, Any]:
        ...

    def collect_capacity(self, tenant_id: str) -> Dict[str, Any]:
        ...


class ReliabilityIntelligenceProviderRegistry:
    """Registry managing domain providers for reliability intelligence."""

    def __init__(self) -> None:
        self._providers: Dict[str, ReliabilityIntelligenceProvider] = {}

    def register_provider(self, domain: Union[str, Enum], provider: ReliabilityIntelligenceProvider) -> None:
        domain_key = domain.value if isinstance(domain, Enum) else str(domain)
        self._providers[domain_key.lower()] = provider
        logger.info(f"Registered ReliabilityIntelligenceProvider for domain: {domain_key}")

    def get_provider(self, domain: Union[str, Enum]) -> Optional[ReliabilityIntelligenceProvider]:
        domain_key = domain.value if isinstance(domain, Enum) else str(domain)
        return self._providers.get(domain_key.lower())

    def list_domains(self) -> List[str]:
        return list(self._providers.keys())


class MockReliabilityIntelligenceProvider:
    """Mock implementation of ReliabilityIntelligenceProvider for testing and fallback."""

    def __init__(self, domain: str = "operations", health_score: float = 0.96) -> None:
        self.domain = domain
        self.health_score = health_score

    def get_provider_name(self) -> str:
        return f"mock_{self.domain}_reliability_provider"

    def get_domain(self) -> str:
        return self.domain

    def collect_signals(self, tenant_id: str) -> List[Dict[str, Any]]:
        return [{"signal_id": f"rel_sig_{self.domain}_01", "status": "OK", "latency_ms": 12.5}]

    def collect_health(self, tenant_id: str) -> Dict[str, Any]:
        return {"status": "HEALTHY", "score": self.health_score, "domain": self.domain}

    def collect_metrics(self, tenant_id: str) -> Dict[str, Any]:
        return {"availability": 0.999, "error_rate": 0.0001, "p99_latency": 45.0}

    def collect_failures(self, tenant_id: str) -> List[Dict[str, Any]]:
        return []

    def collect_incidents(self, tenant_id: str) -> List[Dict[str, Any]]:
        return []

    def collect_dependencies(self, tenant_id: str) -> List[Dict[str, Any]]:
        return [{"target": f"{self.domain}_db", "criticality": "HIGH"}]

    def collect_risk(self, tenant_id: str) -> Dict[str, Any]:
        return {"overall_risk": 0.05, "category": "LOW"}

    def collect_assurance(self, tenant_id: str) -> float:
        return self.health_score

    def collect_trust(self, tenant_id: str) -> Dict[str, Any]:
        return {"trust_score": self.health_score, "level": "HIGH"}

    def collect_capacity(self, tenant_id: str) -> Dict[str, Any]:
        return {"headroom_pct": 45.0, "saturation": 0.55}
