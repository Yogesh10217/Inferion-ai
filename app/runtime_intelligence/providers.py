"""Provider-decoupled architecture for Runtime Intelligence (Phase 5.57)."""

import logging
from typing import Dict, Any, List, Optional
from app.runtime_intelligence.exceptions import RuntimeProviderException

logger = logging.getLogger(__name__)


class RuntimeIntelligenceProvider:
    """Abstract protocol interface for external domain intelligence collection."""

    def __init__(self, domain: str) -> None:
        self.domain = domain

    def collect_runtime_signals(self, tenant_id: str) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def collect_health(self, tenant_id: str) -> Dict[str, Any]:
        raise NotImplementedError

    def collect_risks(self, tenant_id: str) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def collect_assurance(self, tenant_id: str) -> Dict[str, Any]:
        raise NotImplementedError

    def collect_metrics(self, tenant_id: str) -> Dict[str, Any]:
        raise NotImplementedError

    def collect_intelligence(self, tenant_id: str) -> Dict[str, Any]:
        """Aggregate cross-domain intelligence summary."""
        raise NotImplementedError


class MockRuntimeIntelligenceProvider(RuntimeIntelligenceProvider):
    """Mock implementation providing fault-isolated domain intelligence."""

    def collect_runtime_signals(self, tenant_id: str) -> List[Dict[str, Any]]:
        return [
            {
                "signal_type": "PERFORMANCE",
                "severity": "INFO",
                "domain": self.domain,
                "payload": {"latency_ms": 42.0, "throughput_qps": 250},
            }
        ]

    def collect_health(self, tenant_id: str) -> Dict[str, Any]:
        return {"status": "HEALTHY", "score": 0.95, "domain": self.domain}

    def collect_risks(self, tenant_id: str) -> List[Dict[str, Any]]:
        return [{"risk_level": "LOW", "factor": f"{self.domain}_nominal"}]

    def collect_assurance(self, tenant_id: str) -> Dict[str, Any]:
        return {"assurance_score": 0.96, "posture": "ASSURED", "domain": self.domain}

    def collect_metrics(self, tenant_id: str) -> Dict[str, Any]:
        return {"error_rate": 0.001, "cpu_usage": 0.35, "domain": self.domain}

    def collect_intelligence(self, tenant_id: str) -> Dict[str, Any]:
        """Aggregate intelligence dictionary for provider domain."""
        return {
            "domain": self.domain,
            "status": "HEALTHY",
            "score": 0.95,
            "signals": self.collect_runtime_signals(tenant_id),
            "health": self.collect_health(tenant_id),
            "risks": self.collect_risks(tenant_id),
            "assurance": self.collect_assurance(tenant_id),
            "metrics": self.collect_metrics(tenant_id),
        }


class RuntimeIntelligenceProviderRegistry:
    """Thread-safe registry for domain intelligence providers with fault isolation."""

    def __init__(self) -> None:
        self._providers: Dict[str, RuntimeIntelligenceProvider] = {}

    def register_provider(self, domain: str, provider: RuntimeIntelligenceProvider) -> None:
        self._providers[domain] = provider
        logger.info(f"Registered RuntimeIntelligenceProvider for domain: {domain}")

    def get_provider(self, domain: str) -> Optional[RuntimeIntelligenceProvider]:
        return self._providers.get(domain)

    def list_domains(self) -> List[str]:
        return list(self._providers.keys())

    def collect_all_signals(self, tenant_id: str) -> List[Dict[str, Any]]:
        signals: List[Dict[str, Any]] = []
        for domain, provider in self._providers.items():
            try:
                domain_signals = provider.collect_runtime_signals(tenant_id)
                signals.extend(domain_signals)
            except Exception as e:
                logger.warning(f"Provider fault isolated for domain '{domain}': {e}")
        return signals
