from app.providers.openai_provider import OpenAIProvider
from app.providers.provider_factory import ProviderFactory


def test_factory_registers_and_resolves_builtin_provider() -> None:
    factory = ProviderFactory()
    factory.register_provider("openai", OpenAIProvider)

    assert factory.provider_exists("openai") is True
    assert "openai" in factory.list_providers()
    assert isinstance(factory.get_provider("openai"), OpenAIProvider)


def test_factory_supports_callable_registration() -> None:
    class DummyProvider(OpenAIProvider):
        name = "dummy"

    factory = ProviderFactory()
    factory.register_provider("dummy", lambda: DummyProvider())

    assert factory.provider_exists("dummy") is True
    provider = factory.get_provider("dummy")
    assert isinstance(provider, DummyProvider)
    assert provider.name == "dummy"
