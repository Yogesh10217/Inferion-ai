import math
from abc import ABC, abstractmethod
from typing import List


class EmbeddingProvider(ABC):
    """Abstract base class for vector embedding generation."""

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Generate a vector embedding for input text."""
        raise NotImplementedError


class DummyEmbeddingProvider(EmbeddingProvider):
    """Deterministic mock embedding provider for local testing and offline use."""

    def __init__(self, dimension: int = 64) -> None:
        self.dimension = dimension

    async def embed(self, text: str) -> List[float]:
        vec = [0.0] * self.dimension
        for i, char in enumerate(text[: self.dimension]):
            vec[i % self.dimension] += ord(char) / 255.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI vector embedding provider via HTTP API."""

    def __init__(self, api_key: str | None = None, model: str = "text-embedding-3-small") -> None:
        self.api_key = api_key
        self.model = model

    async def embed(self, text: str) -> List[float]:
        if not self.api_key:
            return await DummyEmbeddingProvider().embed(text)

        import httpx

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"input": text, "model": self.model},
                timeout=10.0,
            )
            if resp.status_code == 200:
                data = resp.json()
                return data["data"][0]["embedding"]
            return await DummyEmbeddingProvider().embed(text)
