"""Continuous assurance cross-domain coordinator (Phase 5.54)."""

import logging
from typing import Any, Dict

from app.continuous_assurance.providers import ContinuousAssuranceProviderRegistry

logger = logging.getLogger(__name__)


class ContinuousAssuranceCoordinator:
    """Coordinates cross-domain insights via provider registry without direct manager imports."""

    def __init__(self, provider_registry: ContinuousAssuranceProviderRegistry) -> None:
        self.provider_registry = provider_registry

    def coordinate_domain_assurance(self, tenant_id: str) -> Dict[str, Any]:
        domains = self.provider_registry.list_domains()
        results = {}
        for domain in domains:
            provider = self.provider_registry.get_provider(domain)
            if provider:
                results[domain] = provider.get_assurance_score(tenant_id)
        return {"tenant_id": tenant_id, "domain_scores": results}
