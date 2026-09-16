"""
Provider Protocol & Registry for Platform Hardening.
Provides fault-isolated collection across all platform providers.
"""

import concurrent.futures
import logging
import time
from typing import Dict, List, Optional, Protocol, runtime_checkable

from app.platform_hardening.exceptions import (
    ProviderContractViolationException,
)
from app.platform_hardening.models import (
    EngineConnectionStatus,
    IntegrationHealthStatus,
    ProviderIntegrationStatus,
    SubsystemIntegrationStatus,
)

logger = logging.getLogger(__name__)


@runtime_checkable
class PlatformHardeningProvider(Protocol):
    """Protocol contract for platform phase providers."""

    def collect_integration_status(self) -> SubsystemIntegrationStatus:
        ...

    def collect_context(self) -> Dict:
        ...

    def collect_traceability(self) -> Dict:
        ...

    def collect_lineage(self) -> Dict:
        ...

    def collect_governance(self) -> Dict:
        ...

    def collect_delegations(self) -> Dict:
        ...

    def collect_verifications(self) -> Dict:
        ...

    def collect_evidence(self) -> Dict:
        ...

    def collect_health(self) -> IntegrationHealthStatus:
        ...

    def collect_engine_status(self) -> List[EngineConnectionStatus]:
        ...


class PlatformHardeningProviderRegistry:
    """Registry maintaining registered phase providers with timeout & exception isolation."""

    def __init__(self, timeout_seconds: float = 2.0):
        self._providers: Dict[str, PlatformHardeningProvider] = {}
        self._timeout_seconds = timeout_seconds

    def register_provider(self, provider_id: str, provider: PlatformHardeningProvider):
        self.validate_provider_contract(provider)
        self._providers[provider_id] = provider

    def unregister_provider(self, provider_id: str):
        if provider_id in self._providers:
            del self._providers[provider_id]

    def get_provider(self, provider_id: str) -> Optional[PlatformHardeningProvider]:
        return self._providers.get(provider_id)

    def list_registered_providers(self) -> List[str]:
        return list(self._providers.keys())

    def validate_provider_contract(self, provider: PlatformHardeningProvider):
        required_methods = [
            "collect_integration_status",
            "collect_context",
            "collect_traceability",
            "collect_lineage",
            "collect_governance",
            "collect_delegations",
            "collect_verifications",
            "collect_evidence",
            "collect_health",
            "collect_engine_status",
        ]
        for m in required_methods:
            if not hasattr(provider, m) or not callable(getattr(provider, m)):
                raise ProviderContractViolationException(
                    f"Provider missing required method '{m}'"
                )

    def check_provider_health(self, provider_id: str) -> ProviderIntegrationStatus:
        provider = self.get_provider(provider_id)
        if not provider:
            return ProviderIntegrationStatus(
                provider_id=provider_id,
                subsystem_name=provider_id,
                is_registered=False,
                is_healthy=False,
                response_time_ms=0.0,
                timeout_protected=True,
                exception_isolated=True,
                contract_valid=False,
                error_detail="Provider not registered",
            )

        start_time = time.perf_counter()
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(provider.collect_health)
                health_status = future.result(timeout=self._timeout_seconds)
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0

                is_healthy = health_status in [
                    IntegrationHealthStatus.HEALTHY,
                    IntegrationHealthStatus.DEGRADED,
                ]

                return ProviderIntegrationStatus(
                    provider_id=provider_id,
                    subsystem_name=provider_id,
                    is_registered=True,
                    is_healthy=is_healthy,
                    response_time_ms=elapsed_ms,
                    timeout_protected=True,
                    exception_isolated=True,
                    contract_valid=True,
                    confidence_degraded=(health_status == IntegrationHealthStatus.DEGRADED),
                    freshness_seconds=0.0,
                )

        except concurrent.futures.TimeoutError:
            logger.warning(f"Provider {provider_id} health check timed out after {self._timeout_seconds}s")
            return ProviderIntegrationStatus(
                provider_id=provider_id,
                subsystem_name=provider_id,
                is_registered=True,
                is_healthy=False,
                response_time_ms=self._timeout_seconds * 1000.0,
                timeout_protected=True,
                exception_isolated=True,
                contract_valid=True,
                error_detail=f"Timeout after {self._timeout_seconds}s",
            )
        except Exception as e:
            logger.error(f"Provider {provider_id} health check failed with exception: {e}")
            return ProviderIntegrationStatus(
                provider_id=provider_id,
                subsystem_name=provider_id,
                is_registered=True,
                is_healthy=False,
                response_time_ms=0.0,
                timeout_protected=True,
                exception_isolated=True,
                contract_valid=True,
                error_detail=str(e),
            )

    def collect_all_provider_results(self) -> Dict[str, Dict]:
        """Collects provider data across all registered providers with fault isolation."""
        results = {}
        for provider_id, provider in self._providers.items():
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    def _collect():
                        return {
                            "integration_status": provider.collect_integration_status(),
                            "context": provider.collect_context(),
                            "traceability": provider.collect_traceability(),
                            "lineage": provider.collect_lineage(),
                            "governance": provider.collect_governance(),
                            "delegations": provider.collect_delegations(),
                            "verifications": provider.collect_verifications(),
                            "evidence": provider.collect_evidence(),
                            "health": provider.collect_health(),
                            "engine_status": provider.collect_engine_status(),
                        }
                    future = executor.submit(_collect)
                    res = future.result(timeout=self._timeout_seconds)
                    results[provider_id] = res
            except Exception as e:
                logger.error(f"Provider {provider_id} collection failed: {e}")
                results[provider_id] = {
                    "error": str(e),
                    "health": IntegrationHealthStatus.UNHEALTHY,
                }
        return results
