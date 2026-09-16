"""Resource profile management for Capacity Intelligence (Phase 5.56)."""

import logging

from app.capacity_intelligence.models import ResourceProfile

logger = logging.getLogger(__name__)


class ResourceProfileEngine:
    """Manages resource profile registration and capacity definitions."""

    def register_resource(
        self, tenant_id: str, resource_id: str, resource_type: str, total_capacity: float, unit: str = "cores"
    ) -> ResourceProfile:
        prof = ResourceProfile(
            tenant_id=tenant_id,
            resource_id=resource_id,
            resource_type=resource_type,
            total_capacity=total_capacity,
            unit=unit,
        )
        logger.info(f"Registered ResourceProfile '{prof.profile_id}' for resource '{resource_id}' ({resource_type})")
        return prof
