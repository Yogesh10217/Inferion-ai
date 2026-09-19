from __future__ import annotations

from typing import Callable

from app.providers.base_provider import BaseProvider


class ProviderFactory:
    """Registry and factory for provider instances.

    The factory accepts either provider classes or callables that return an
    instance of a provider. This keeps provider selection open for future
    integrations such as Gemini, Claude, Groq, or Hugging Face without changing
    the surrounding service code.
    """

    def __init__(self) -> None:
        self._providers: dict[str, Callable[[], BaseProvider]] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        from app.providers.anthropic_provider import AnthropicProvider
        from app.providers.azure_openai_provider import AzureOpenAIProvider
        from app.providers.bedrock_provider import BedrockProvider
        from app.providers.cohere_provider import CohereProvider
        from app.providers.gemini_provider import GeminiProvider
        from app.providers.mistral_provider import MistralProvider
        from app.providers.ollama_provider import OllamaProvider
        from app.providers.openai_provider import OpenAIProvider

        self.register_provider("openai", OpenAIProvider)
        self.register_provider("ollama", OllamaProvider)
        self.register_provider("anthropic", AnthropicProvider)
        self.register_provider("gemini", GeminiProvider)
        self.register_provider("cohere", CohereProvider)
        self.register_provider("mistral", MistralProvider)
        self.register_provider("bedrock", BedrockProvider)
        self.register_provider("azure_openai", AzureOpenAIProvider)
        self.register_provider("embedding", OpenAIProvider)  # Mock registration
        self.register_provider("reranking", OllamaProvider)  # Mock registration

    def register_provider(self, name: str, provider: type[BaseProvider] | Callable[[], BaseProvider] | BaseProvider) -> None:
        """Register a provider factory by name."""
        if not name or not name.strip():
            raise ValueError("Provider name must be a non-empty string")

        if isinstance(provider, BaseProvider):
            self._providers[name] = lambda: provider
            return

        if isinstance(provider, type):
            if not issubclass(provider, BaseProvider):
                raise TypeError("Provider classes must inherit BaseProvider")
            self._providers[name] = provider
            return

        if callable(provider):
            self._providers[name] = provider
            return

        raise TypeError("Provider must be a BaseProvider instance, provider class, or callable")

    def get_provider(self, name: str) -> BaseProvider:
        """Return an instance of the named provider."""
        if not self.provider_exists(name):
            raise KeyError(f"Unknown provider '{name}'")

        provider_factory = self._providers[name]
        provider = provider_factory()
        if not isinstance(provider, BaseProvider):
            raise TypeError(f"Provider '{name}' did not return a BaseProvider instance")
        return provider

    def list_providers(self) -> list[str]:
        """Return the names of all registered providers."""
        return sorted(self._providers.keys())

    def provider_exists(self, name: str) -> bool:
        """Return whether a provider has been registered."""
        return name in self._providers
