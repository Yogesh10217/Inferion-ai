from app.providers.base_provider import BaseProvider


class OpenAIProvider(BaseProvider):
    """Placeholder provider for OpenAI-compatible backends."""

    async def invoke(self, prompt: str) -> str:
        return f"OpenAI placeholder response for: {prompt}"

    async def health_check(self) -> bool:
        return True
