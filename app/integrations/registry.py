"""Integration Registry & Catalog Subsystem."""

import logging
from typing import Any, Dict, List, Optional

from app.integrations.exceptions import IntegrationNotFoundException
from app.integrations.integration import Integration, IntegrationStatus, IntegrationType

logger = logging.getLogger(__name__)


class IntegrationRegistry:
    """Manages registration, capability discovery, versioning, and status transitions for integrations."""

    def __init__(self) -> None:
        self._integrations: Dict[str, Integration] = {}

    def register_integration(
        self,
        name: str,
        category: IntegrationType = IntegrationType.SAAS,
        tenant_id: str = "global",
        config: Optional[Dict[str, Any]] = None,
        credential_id: Optional[str] = None,
    ) -> Integration:
        integ = Integration(
            name=name,
            category=category,
            tenant_id=tenant_id,
            config=config or {},
            credential_id=credential_id,
        )
        self._integrations[integ.integration_id] = integ
        logger.info(f"[INTEGRATION REGISTRY] Registered integration '{integ.integration_id}' ('{name}', {category.value}) for tenant '{tenant_id}'")
        return integ

    def get_integration(self, integration_id: str) -> Integration:
        integ = self._integrations.get(integration_id)
        if not integ or integ.status == IntegrationStatus.ARCHIVED:
            raise IntegrationNotFoundException(integration_id)
        return integ

    def update_status(self, integration_id: str, new_status: IntegrationStatus) -> Integration:
        integ = self.get_integration(integration_id)
        integ.status = new_status
        logger.info(f"[INTEGRATION REGISTRY] Integration '{integration_id}' status updated -> {new_status.value}")
        return integ

    def list_integrations(self, tenant_id: Optional[str] = None, category: Optional[IntegrationType] = None) -> List[Integration]:
        res = [i for i in self._integrations.values() if i.status != IntegrationStatus.ARCHIVED]
        if tenant_id:
            res = [r for r in res if r.tenant_id == tenant_id]
        if category:
            res = [r for r in res if r.category == category]
        return res
