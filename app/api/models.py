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


@router.post("/models")
async def register_model(
    payload: dict,
    registry_instance: ModelRegistry = Depends(get_model_registry),
):
    """Register a new model in the Inference Gateway Model Registry via API/UI."""
    from app.registry.model_metadata import ModelMetadata

    model_id = payload.get("id") or payload.get("name") or "custom-model"
    provider = payload.get("provider") or "custom"
    context_window = payload.get("context_window", 128000)
    description = payload.get("description", f"{provider} {model_id}")

    model_meta = ModelMetadata(
        id=model_id,
        provider=provider,
        description=description,
        context_window=context_window,
        status="available",
    )
    saved = registry_instance.register_model(model_meta)
    return {
        "status": "success",
        "message": f"Model '{model_id}' registered successfully",
        "model": {
            "id": saved.id,
            "provider": saved.provider,
            "context_window": saved.context_window,
            "status": saved.status,
        },
    }


@router.delete("/models/{model_id}")
async def delete_model(
    model_id: str,
    registry_instance: ModelRegistry = Depends(get_model_registry),
):
    """Unregister/delete a model from the Inference Gateway Model Registry."""
    registry_instance.unregister_model(model_id)
    return {
        "status": "success",
        "message": f"Model '{model_id}' unregistered successfully",
        "model_id": model_id,
    }
