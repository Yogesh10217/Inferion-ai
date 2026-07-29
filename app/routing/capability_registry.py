import threading
from typing import Dict, Set, List, Optional


class CapabilityRegistry:
    """Dynamic provider capability mapping and filtering."""

    STANDARD_CAPABILITIES = {
        "chat",
        "streaming",
        "vision",
        "embeddings",
        "function_calling",
        "tools",
    }

    def __init__(self):
        self._lock = threading.RLock()
        self._provider_capabilities: Dict[str, Set[str]] = {}
        self._provider_models: Dict[str, Set[str]] = {}

    def register(
        self,
        provider_id: str,
        capabilities: List[str],
        models: Optional[List[str]] = None,
    ) -> None:
        """Register capabilities and supported models for a provider."""
        with self._lock:
            self._provider_capabilities[provider_id] = set(capabilities)
            if models is not None:
                self._provider_models[provider_id] = set(models)

    def unregister(self, provider_id: str) -> None:
        """Unregister a provider."""
        with self._lock:
            self._provider_capabilities.pop(provider_id, None)
            self._provider_models.pop(provider_id, None)

    def get_capabilities(self, provider_id: str) -> Set[str]:
        """Get capabilities set for a given provider."""
        with self._lock:
            return set(self._provider_capabilities.get(provider_id, set()))

    def has_capability(self, provider_id: str, capability: str) -> bool:
        """Check if provider has specific capability."""
        with self._lock:
            return capability in self._provider_capabilities.get(provider_id, set())

    def filter_providers_by_capabilities(
        self, providers: List[str], required_capabilities: List[str]
    ) -> List[str]:
        """Filter a list of providers to only those matching all required capabilities."""
        if not required_capabilities:
            return list(providers)
        req_set = set(required_capabilities)
        with self._lock:
            return [
                p for p in providers
                if req_set.issubset(self._provider_capabilities.get(p, set()))
            ]

    def get_providers_with_capability(self, capability: str) -> List[str]:
        """Get all registered providers supporting a specific capability."""
        with self._lock:
            return [
                p for p, caps in self._provider_capabilities.items()
                if capability in caps
            ]

    def supports_model(self, provider_id: str, model_id: str) -> bool:
        """Check if provider explicitly supports a given model ID."""
        with self._lock:
            models = self._provider_models.get(provider_id)
            if models is None:
                # If not registered explicitly, assume provider supports model
                return True
            return model_id in models or "*" in models

    def get_all(self) -> Dict[str, List[str]]:
        """Retrieve all registered providers and their capabilities."""
        with self._lock:
            return {p: sorted(list(caps)) for p, caps in self._provider_capabilities.items()}
