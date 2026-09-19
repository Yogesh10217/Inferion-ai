from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.providers.base_provider import BaseProvider
from app.routing.provider_health import ProviderHealthMonitor


@dataclass
class ProviderInstance:
    """Represents a specific, routable instance of a provider."""

    provider_id: str
    instance_id: str
    provider: BaseProvider
    base_url: Optional[str] = None
    weight: int = 1
    priority: int = 0
    region: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    health: ProviderHealthMonitor = field(default_factory=ProviderHealthMonitor)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProviderPool:
    """Maintains a collection of provider instances grouped by provider ID."""

    def __init__(self) -> None:
        self._instances: Dict[str, List[ProviderInstance]] = {}

    def register_instance(self, instance: ProviderInstance) -> None:
        """Register a new provider instance."""
        if instance.provider_id not in self._instances:
            self._instances[instance.provider_id] = []

        # Avoid duplicate registration
        existing = [inst for inst in self._instances[instance.provider_id] if inst.instance_id == instance.instance_id]
        if not existing:
            self._instances[instance.provider_id].append(instance)

    def remove_instance(self, provider_id: str, instance_id: str) -> None:
        """Remove a provider instance."""
        if provider_id in self._instances:
            self._instances[provider_id] = [
                inst for inst in self._instances[provider_id] if inst.instance_id != instance_id
            ]

    def get_instances(self, provider_id: str) -> List[ProviderInstance]:
        """Get all registered instances for a given provider."""
        return self._instances.get(provider_id, [])

    def get_healthy_instances(self, provider_id: str) -> List[ProviderInstance]:
        """Get all currently healthy instances for a provider."""
        instances = self.get_instances(provider_id)
        return [inst for inst in instances if inst.health.is_healthy()]
