from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.tracing.sampling import AlwaysOffSampler, AlwaysOnSampler, TraceIdRatioBasedSampler
from app.tracing.tracer import TracerProvider, get_tracer_provider

router = APIRouter(prefix="/tracing", tags=["tracing"])


class TracingConfigUpdateSchema(BaseModel):
    exporter: Optional[str] = None
    sample_ratio: Optional[float] = None
    environment: Optional[str] = None


class SwitchExporterSchema(BaseModel):
    name: str


@router.get("/config")
async def get_config(provider: TracerProvider = Depends(get_tracer_provider)):
    """Retrieve active OpenTelemetry tracing configuration."""
    active_exporter = provider.exporter_registry._active_name
    return {
        "service_name": provider.resource_attributes.get("service.name"),
        "service_version": provider.resource_attributes.get("service.version"),
        "environment": provider.resource_attributes.get("deployment.environment"),
        "active_exporter": active_exporter,
        "sampler_type": type(provider.sampler).__name__,
        "resource_attributes": provider.resource_attributes,
    }


@router.put("/config")
async def update_config(
    data: TracingConfigUpdateSchema,
    provider: TracerProvider = Depends(get_tracer_provider),
):
    """Update dynamic tracing configuration (exporters, sample ratio, environment)."""
    if data.exporter:
        try:
            provider.set_exporter(data.exporter)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if data.sample_ratio is not None:
        if data.sample_ratio >= 1.0:
            provider.sampler = AlwaysOnSampler()
        elif data.sample_ratio <= 0.0:
            provider.sampler = AlwaysOffSampler()
        else:
            provider.sampler = TraceIdRatioBasedSampler(data.sample_ratio)

    if data.environment:
        provider.resource_attributes["deployment.environment"] = data.environment

    return await get_config(provider)


@router.get("/exporters")
async def list_exporters(provider: TracerProvider = Depends(get_tracer_provider)):
    """List available exporters and active selection."""
    return {
        "active_exporter": provider.exporter_registry._active_name,
        "available_exporters": provider.exporter_registry.list_exporters(),
    }


@router.post("/exporters")
async def set_exporter(
    data: SwitchExporterSchema,
    provider: TracerProvider = Depends(get_tracer_provider),
):
    """Switch active span exporter."""
    try:
        provider.set_exporter(data.name)
        return {"status": "updated", "active_exporter": data.name}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/sampling")
async def get_sampling_config(provider: TracerProvider = Depends(get_tracer_provider)):
    """Retrieve current sampling configuration."""
    sampler_type = type(provider.sampler).__name__
    ratio = getattr(provider.sampler, "ratio", 1.0 if sampler_type == "AlwaysOnSampler" else 0.0)
    return {
        "sampler_type": sampler_type,
        "sample_ratio": ratio,
    }
