from fastapi import APIRouter, Request, Response
from app.core.container import ServiceContainer

router = APIRouter(tags=["Metrics"])

@router.get("/metrics")
async def get_metrics(request: Request) -> Response:
    """Expose Prometheus-compatible metrics."""
    container: ServiceContainer = request.app.state.container
    if not container.prometheus_exporter:
        return Response(content="Prometheus metrics are disabled.", status_code=404)
        
    payload, content_type = container.prometheus_exporter.export()
    return Response(content=payload, media_type=content_type)
