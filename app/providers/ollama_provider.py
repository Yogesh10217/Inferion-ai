from app.providers.base_provider import BaseProvider


class OllamaProvider(BaseProvider):
    """Placeholder provider for Ollama-compatible backends."""

    async def invoke(self, prompt: str) -> str:
        return f"Ollama placeholder response for: {prompt}"

    async def health_check(self) -> bool:
        return True
