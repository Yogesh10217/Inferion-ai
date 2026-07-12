from dataclasses import dataclass


@dataclass(slots=True)
class RegisteredModel:
    id: str
    provider: str
    version: str = "latest"


class InMemoryModelRegistry:
    """Simple in-memory registry for Phase 1 scaffolding."""

    def __init__(self) -> None:
        self._models: dict[str, RegisteredModel] = {}
        self._seed()

    def _seed(self) -> None:
        self._models["gpt-4o-mini"] = RegisteredModel(id="gpt-4o-mini", provider="openai")
        self._models["llama3.1"] = RegisteredModel(id="llama3.1", provider="ollama")

    def list_models(self) -> list[dict[str, str]]:
        return [
            {"id": model.id, "provider": model.provider, "version": model.version}
            for model in self._models.values()
        ]
