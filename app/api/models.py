from fastapi import APIRouter, Depends, Request

from app.registry.model_registry import InMemoryModelRegistry
from app.registry.repository import ModelRegistry
from app.schemas.response import ModelInfo, ModelListResponse

router = APIRouter(tags=["models"])
registry = InMemoryModelRegistry()


def get_model_registry(request: Request) -> ModelRegistry:
    """Dependency injection provider for the model registry."""
    if hasattr(request.app.state, "container"):
        return request.app.state.container.registry
    return registry


@router.get("/models", response_model=ModelListResponse)
async def list_models(registry_instance: ModelRegistry = Depends(get_model_registry)) -> ModelListResponse:
    """List available models in an OpenAI-compatible format."""
    models = [
        ModelInfo(
            id=model.id,
            object="model",
            created=0,
            owned_by=model.provider,
        )
        for model in registry_instance.list_models()
    ]
    return ModelListResponse(object="list", data=models)
