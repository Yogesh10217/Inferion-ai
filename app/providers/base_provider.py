from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """Abstract contract for inference providers."""

    @abstractmethod
    async def invoke(self, prompt: str) -> str:
        """Invoke the provider with a prompt."""
        raise NotImplementedError

    @abstractmethod
    async def health_check(self) -> bool:
        """Check whether the provider is healthy."""
        raise NotImplementedError
