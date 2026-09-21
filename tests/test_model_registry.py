import pytest

from app.registry.model_metadata import RegisteredModel
from app.registry.model_registry import InMemoryModelRegistry


@pytest.fixture
def registry() -> InMemoryModelRegistry:
    return InMemoryModelRegistry()


def test_register_and_get_model(registry: InMemoryModelRegistry) -> None:
    model = RegisteredModel(
        id="mistral-small",
        provider="ollama",
        description="Local mistral model",
        context_window=16384,
        status="available",
    )

    saved = registry.register_model(model)

    assert saved.id == model.id
    assert registry.get_model("mistral-small") == model
    assert registry.model_exists("mistral-small") is True


def test_unregister_model(registry: InMemoryModelRegistry) -> None:
    model = RegisteredModel(
        id="mistral-small",
        provider="ollama",
        description="Local mistral model",
        context_window=16384,
        status="available",
    )

    registry.register_model(model)
    registry.unregister_model("mistral-small")

    assert registry.get_model("mistral-small") is None
    assert registry.model_exists("mistral-small") is False


def test_list_models_returns_seeded_and_registered_models(registry: InMemoryModelRegistry) -> None:
    models = registry.list_models()

    ids = {item.id for item in models}
    assert {"gpt-4o-mini", "llama3.1"}.issubset(ids)

    model = RegisteredModel(
        id="mistral-small",
        provider="ollama",
        description="Local mistral model",
        context_window=16384,
        status="available",
    )
    registry.register_model(model)

    updated_models = registry.list_models()
    assert "mistral-small" in {item.id for item in updated_models}
