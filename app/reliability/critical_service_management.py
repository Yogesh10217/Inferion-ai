"""
Phase 5.70 - Critical Service Management Module.

Manages platform service catalog, criticality tiers, dependencies, and recovery sequence ordering.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class ServiceCriticality(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class CriticalService:
    service_id: str
    name: str
    criticality: ServiceCriticality
    priority: int  # Lower number = higher recovery priority (e.g. 1 is first)
    dependencies: List[str] = field(default_factory=list)
    recovery_order: int = 1
    minimum_functionality: str = "Core API & Auth operational"
    max_downtime_seconds: float = 300.0  # 5 minutes


class CriticalServiceManager:
    """Manages critical services, priorities, and dependency-ordered recovery sequences."""

    def __init__(self) -> None:
        self._services: Dict[str, CriticalService] = {}

    def register_service(self, service: CriticalService) -> None:
        self._services[service.service_id] = service

    def get_service(self, service_id: str) -> Optional[CriticalService]:
        return self._services.get(service_id)

    def list_services(self) -> List[CriticalService]:
        return list(self._services.values())

    def get_recovery_sequence(self) -> List[CriticalService]:
        """Sorts services by priority (ascending) and recovery order."""
        services = list(self._services.values())
        return sorted(services, key=lambda s: (s.priority, s.recovery_order, s.service_id))

    def get_critical_services(self) -> List[CriticalService]:
        return [s for s in self._services.values() if s.criticality == ServiceCriticality.CRITICAL]
