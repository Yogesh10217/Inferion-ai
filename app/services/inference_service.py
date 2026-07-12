from app.providers.base_provider import BaseProvider
from app.registry.model_registry import InMemoryModelRegistry


class InferenceService:
    """Service that coordinates provider invocation for a request."""

    def __init__(self, registry: InMemoryModelRegistry, provider: BaseProvider) -> None:
        self._registry = registry
        self._provider = provider

    async def complete(self, model_id: str, prompt: str) -> str:
        if model_id not in {model["id"] for model in self._registry.list_models()}:
            raise ValueError(f"Unknown model: {model_id}")
        return await self._provider.invoke(prompt)
