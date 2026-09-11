from __future__ import annotations

from typing import Dict, List, Optional

from app.core.container import ServiceContainer


class PlatformServiceRegistry:
    """Validates registration and availability of existing upper platform managers in ServiceContainer."""

    EXPECTED_MANAGERS = [
        "unified_intelligence_manager",
        "decision_intelligence_manager",
        "autonomous_assurance_manager",
        "continuous_assurance_manager",
        "reliability_intelligence_manager",
        "capacity_intelligence_manager",
        "runtime_intelligence_manager",
        "platform_integration_manager",
        "platform_hardening_manager",
    ]

    @classmethod
    def validate_platform_managers(cls, container: Optional[ServiceContainer]) -> Dict[str, bool]:
        if container is None:
            return {manager: False for manager in cls.EXPECTED_MANAGERS}

        status: Dict[str, bool] = {}
        for manager_attr in cls.EXPECTED_MANAGERS:
            instance = getattr(container, manager_attr, None)
            status[manager_attr] = instance is not None
        return status

    @classmethod
    def get_registered_manager_names(cls, container: Optional[ServiceContainer]) -> List[str]:
        if container is None:
            return []
        registered = []
        for manager_attr in cls.EXPECTED_MANAGERS:
            if getattr(container, manager_attr, None) is not None:
                registered.append(manager_attr)
        return registered
