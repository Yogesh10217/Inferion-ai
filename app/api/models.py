from fastapi import APIRouter

from app.registry.model_registry import InMemoryModelRegistry
from app.schemas.response import ModelInfo, ModelListResponse

router = APIRouter(tags=["models"])
registry = InMemoryModelRegistry()


@router.get("/models", response_model=ModelListResponse)
async def list_models() -> ModelListResponse:
    """List available models in an OpenAI-compatible format."""
    models = [
        ModelInfo(
            id=model.id,
            object="model",
            created=0,
            owned_by=model.provider,
        )
        for model in registry.list_models()
    ]
    return ModelListResponse(object="list", data=models)
