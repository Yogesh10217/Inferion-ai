"""Provider-decoupled architecture for Continuous Assurance (Phase 5.54)."""

import logging
from typing import Dict, Any, Optional, Protocol, List, Union, runtime_checkable
from enum import Enum

logger = logging.getLogger(__name__)


@runtime_checkable
class ContinuousAssuranceProvider(Protocol):
    """Protocol for cross-domain assurance data providers."""

    def get_provider_name(self) -> str:
        ...

    def get_domain(self) -> str:
        ...

    def get_runtime_signals(self, tenant_id: str, scope: Optional[str] = None) -> List[Dict[str, Any]]:
        ...

    def get_assurance_score(self, tenant_id: str) -> float:
        ...

    def get_trust_assessment(self, tenant_id: str) -> Dict[str, Any]:
        ...

    def get_risk_profile(self, tenant_id: str) -> Dict[str, Any]:
        ...

    def get_policy_evaluation(self, tenant_id: str) -> Dict[str, Any]:
        ...

    def get_verification_results(self, tenant_id: str) -> List[Dict[str, Any]]:
        ...


class ContinuousAssuranceProviderRegistry:
    """Registry managing domain providers for continuous assurance."""

    def __init__(self) -> None:
        self._providers: Dict[str, ContinuousAssuranceProvider] = {}

    def register_provider(self, domain: Union[str, Enum], provider: ContinuousAssuranceProvider) -> None:
        domain_key = domain.value if isinstance(domain, Enum) else str(domain)
        self._providers[domain_key.lower()] = provider
        logger.info(f"Registered ContinuousAssuranceProvider for domain: {domain_key}")

    def get_provider(self, domain: Union[str, Enum]) -> Optional[ContinuousAssuranceProvider]:
        domain_key = domain.value if isinstance(domain, Enum) else str(domain)
        return self._providers.get(domain_key.lower())

    def list_domains(self) -> List[str]:
        return list(self._providers.keys())


class MockContinuousAssuranceProvider:
    """Mock implementation of ContinuousAssuranceProvider for testing and fallback."""

    def __init__(self, domain: str = "security", score: float = 0.92) -> None:
        self.domain = domain
        self.score = score

    def get_provider_name(self) -> str:
        return f"mock_{self.domain}_provider"

    def get_domain(self) -> str:
        return self.domain

    def get_runtime_signals(self, tenant_id: str, scope: Optional[str] = None) -> List[Dict[str, Any]]:
        return [
            {"signal_id": f"sig_{self.domain}_01", "type": f"{self.domain}_event", "status": "OK", "value": 0.95}
        ]

    def get_assurance_score(self, tenant_id: str) -> float:
        return self.score

    def get_trust_assessment(self, tenant_id: str) -> Dict[str, Any]:
        return {"trust_score": self.score, "confidence": 0.9, "level": "HIGH"}

    def get_risk_profile(self, tenant_id: str) -> Dict[str, Any]:
        return {"overall_risk": 0.15, "category": "LOW"}

    def get_policy_evaluation(self, tenant_id: str) -> Dict[str, Any]:
        return {"compliant": True, "violations_count": 0}

    def get_verification_results(self, tenant_id: str) -> List[Dict[str, Any]]:
        return [{"verification_id": "v_01", "status": "VERIFIED"}]
