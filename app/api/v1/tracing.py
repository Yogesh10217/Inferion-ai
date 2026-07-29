from fastapi import APIRouter
router = APIRouter(prefix="/v1/tracing", tags=["tracing"])

@router.get("/config")
async def get_config():
    return {}

@router.patch("/config")
async def update_config():
    return {}

@router.get("/sampling")
async def get_sampling():
    return {}

@router.get("/exporters")
async def get_exporters():
    return {}
