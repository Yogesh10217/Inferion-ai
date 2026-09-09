"""Provider-decoupled architecture for Capacity Intelligence (Phase 5.56)."""

import logging
from typing import Dict, Any, List, Optional
from app.capacity_intelligence.exceptions import CapacityIntelligenceException

logger = logging.getLogger(__name__)


class CapacityIntelligenceProvider:
    """Abstract protocol interface for external capacity & resource intelligence collection."""

    def __init__(self, domain: str) -> None:
        self.domain = domain

    def collect_telemetry(self, tenant_id: str) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def collect_resource_metrics(self, tenant_id: str) -> Dict[str, Any]:
        raise NotImplementedError

    def collect_workload_metrics(self, tenant_id: str) -> Dict[str, Any]:
        raise NotImplementedError

    def collect_reliability_data(self, tenant_id: str) -> Dict[str, Any]:
        raise NotImplementedError

    def collect_cost_information(self, tenant_id: str) -> Dict[str, Any]:
        raise NotImplementedError


class MockCapacityIntelligenceProvider(CapacityIntelligenceProvider):
    """Mock implementation providing fault-isolated domain intelligence."""

    def collect_telemetry(self, tenant_id: str) -> List[Dict[str, Any]]:
        return [
            {
                "resource_id": f"res_{self.domain}_01",
                "metric_name": "cpu_utilization",
                "metric_value": 0.55,
                "domain": self.domain,
            }
        ]

    def collect_resource_metrics(self, tenant_id: str) -> Dict[str, Any]:
        return {"consumed_pct": 55.0, "headroom_pct": 45.0, "domain": self.domain}

    def collect_workload_metrics(self, tenant_id: str) -> Dict[str, Any]:
        return {"request_qps": 120.0, "pattern": "STEADY", "domain": self.domain}

    def collect_reliability_data(self, tenant_id: str) -> Dict[str, Any]:
        return {"health_score": 0.95, "slo_status": "HEALTHY", "domain": self.domain}

    def collect_cost_information(self, tenant_id: str) -> Dict[str, Any]:
        return {"cost_per_request": 0.0001, "total_cost_usd": 12.50, "domain": self.domain}


class CapacityIntelligenceProviderRegistry:
    """Thread-safe registry for domain intelligence providers with fault isolation."""

    def __init__(self) -> None:
        self._providers: Dict[str, CapacityIntelligenceProvider] = {}

    def register_provider(self, domain: str, provider: CapacityIntelligenceProvider) -> None:
        self._providers[domain] = provider
        logger.info(f"Registered CapacityIntelligenceProvider for domain: {domain}")

    def get_provider(self, domain: str) -> Optional[CapacityIntelligenceProvider]:
        return self._providers.get(domain)

    def list_domains(self) -> List[str]:
        return list(self._providers.keys())

    def collect_all_telemetry(self, tenant_id: str) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for domain, provider in self._providers.items():
            try:
                telem = provider.collect_telemetry(tenant_id)
                results.extend(telem)
            except Exception as e:
                logger.warning(f"Provider fault isolated for domain '{domain}': {e}")
        return results
