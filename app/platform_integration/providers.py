"""Provider-Decoupled Integration Protocol and Registry for Phase 5.58."""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.platform_integration.exceptions import (
    IntegrationProviderNotFoundException,
)

logger = logging.getLogger(__name__)


@dataclass
class PlatformProviderResult:
    """Standardized provider execution result preserving confidence and latency."""
    platform: str
    status: str  # SUCCESS, DEGRADED, FAILED
    data: Dict[str, Any]
    confidence: float
    uncertainty: float
    collected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    latency_ms: float = 0.0
    error: Optional[str] = None
    partial: bool = False


class PlatformIntegrationProvider:
    """Abstract protocol for domain intelligence platform adapters."""

    def __init__(self, platform_name: str) -> None:
        self.platform_name = platform_name

    def collect_intelligence(self, tenant_id: str) -> PlatformProviderResult:
        raise NotImplementedError

    def collect_context(self, tenant_id: str) -> Dict[str, Any]:
        raise NotImplementedError

    def collect_assurance(self, tenant_id: str) -> Dict[str, Any]:
        raise NotImplementedError

    def collect_evidence(self, tenant_id: str) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def collect_recommendations(self, tenant_id: str) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def collect_delegations(self, tenant_id: str) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def collect_snapshots(self, tenant_id: str) -> List[Dict[str, Any]]:
        raise NotImplementedError


class MockPlatformIntegrationProvider(PlatformIntegrationProvider):
    """Fault-isolated mock platform provider supporting customizable behavior and simulation."""

    def __init__(
        self,
        platform_name: str,
        simulate_failure: bool = False,
        simulate_timeout: bool = False,
        simulate_partial: bool = False,
        base_score: float = 0.92,
        base_confidence: float = 0.95,
        base_uncertainty: float = 0.05,
    ) -> None:
        super().__init__(platform_name)
        self.simulate_failure = simulate_failure
        self.simulate_timeout = simulate_timeout
        self.simulate_partial = simulate_partial
        self.base_score = base_score
        self.base_confidence = base_confidence
        self.base_uncertainty = base_uncertainty

    def collect_intelligence(self, tenant_id: str) -> PlatformProviderResult:
        t0 = time.perf_counter()
        if self.simulate_failure:
            latency = (time.perf_counter() - t0) * 1000
            return PlatformProviderResult(
                platform=self.platform_name,
                status="FAILED",
                data={},
                confidence=0.0,
                uncertainty=1.0,
                latency_ms=latency,
                error=f"Simulated failure in provider '{self.platform_name}'",
            )

        if self.simulate_timeout:
            latency = (time.perf_counter() - t0) * 1000
            return PlatformProviderResult(
                platform=self.platform_name,
                status="DEGRADED",
                data={},
                confidence=0.2,
                uncertainty=0.8,
                latency_ms=latency,
                error=f"Timeout contacting platform '{self.platform_name}'",
                partial=True,
            )

        data = {
            "score": self.base_score,
            "status": "HEALTHY" if self.base_score >= 0.75 else "DEGRADED",
            "signals": [
                {
                    "signal_id": f"sig-{self.platform_name.lower()}-1",
                    "type": f"{self.platform_name}_TELEMETRY",
                    "value": 42.0,
                    "severity": "LOW",
                }
            ],
            "findings": [
                {
                    "finding_id": f"find-{self.platform_name.lower()}-1",
                    "title": f"{self.platform_name} nominal condition",
                    "severity": "LOW",
                    "impact": 0.1,
                }
            ],
            "recommendations": [
                {
                    "recommendation_id": f"rec-{self.platform_name.lower()}-1",
                    "action": f"OPTIMIZE_{self.platform_name}",
                    "auto_execute": False,
                }
            ],
        }
        latency = (time.perf_counter() - t0) * 1000
        return PlatformProviderResult(
            platform=self.platform_name,
            status="SUCCESS",
            data=data,
            confidence=self.base_confidence,
            uncertainty=self.base_uncertainty,
            latency_ms=latency,
            partial=self.simulate_partial,
        )

    def collect_context(self, tenant_id: str) -> Dict[str, Any]:
        return {"platform": self.platform_name, "tenant_id": tenant_id, "active_entities": 5}

    def collect_assurance(self, tenant_id: str) -> Dict[str, Any]:
        return {"platform": self.platform_name, "score": self.base_score, "posture": "ASSURED"}

    def collect_evidence(self, tenant_id: str) -> List[Dict[str, Any]]:
        return [{"evidence_id": f"ev-{self.platform_name.lower()}-1", "hash": f"hash_{self.platform_name}"}]

    def collect_recommendations(self, tenant_id: str) -> List[Dict[str, Any]]:
        return [{"action": f"TUNE_{self.platform_name}", "auto_execute": False}]

    def collect_delegations(self, tenant_id: str) -> List[Dict[str, Any]]:
        return []

    def collect_snapshots(self, tenant_id: str) -> List[Dict[str, Any]]:
        return [{"snapshot_id": f"snap-{self.platform_name.lower()}-1", "fingerprint": "abc"}]


class PlatformIntegrationProviderRegistry:
    """Thread-safe registry for cross-phase intelligence providers with fault isolation."""

    def __init__(self) -> None:
        self._providers: Dict[str, PlatformIntegrationProvider] = {}
        self._register_default_providers()

    def _register_default_providers(self) -> None:
        default_domains = [
            "RUNTIME",
            "CAPACITY",
            "RELIABILITY",
            "CONTINUOUS_ASSURANCE",
            "AUTONOMOUS_ASSURANCE",
            "DECISION_INTELLIGENCE",
            "UNIFIED_INTELLIGENCE",
            "SECURITY",
            "OPERATIONS",
        ]
        for d in default_domains:
            self.register_provider(d, MockPlatformIntegrationProvider(platform_name=d))

    def register_provider(self, platform_name: str, provider: PlatformIntegrationProvider) -> None:
        normalized = platform_name.upper()
        self._providers[normalized] = provider
        logger.info(f"Registered PlatformIntegrationProvider for: {normalized}")

    def get_provider(self, platform_name: str) -> PlatformIntegrationProvider:
        normalized = platform_name.upper()
        provider = self._providers.get(normalized)
        if not provider:
            raise IntegrationProviderNotFoundException(f"Provider '{platform_name}' is not registered.")
        return provider

    def list_platforms(self) -> List[str]:
        return list(self._providers.keys())

    def collect_all_intelligence(self, tenant_id: str) -> Dict[str, PlatformProviderResult]:
        """Collects intelligence across all registered providers with strict fault isolation."""
        results: Dict[str, PlatformProviderResult] = {}
        for name, provider in self._providers.items():
            try:
                res = provider.collect_intelligence(tenant_id)
                results[name] = res
            except Exception as e:
                logger.error(f"Provider '{name}' raised unhandled error during collection: {e}")
                results[name] = PlatformProviderResult(
                    platform=name,
                    status="FAILED",
                    data={},
                    confidence=0.0,
                    uncertainty=1.0,
                    error=str(e),
                )
        return results
