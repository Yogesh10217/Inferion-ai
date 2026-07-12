from fastapi import APIRouter

from app.registry.model_registry import InMemoryModelRegistry

router = APIRouter(tags=["models"])
registry = InMemoryModelRegistry()


@router.get("/models")
async def list_models() -> list[dict[str, str]]:
    """List available models."""
    return registry.list_models()
