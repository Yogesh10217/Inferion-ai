"""
A/B Testing Traffic Splitting Middleware.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.mlops.experiments import ExperimentManager
import uuid


class ABTestingMiddleware(BaseHTTPMiddleware):
    """Intercepts inference requests and applies active experiment traffic allocations."""

    def __init__(self, app, experiment_manager: ExperimentManager | None = None):
        super().__init__(app)
        self.experiment_manager = experiment_manager or ExperimentManager()

    async def dispatch(self, request: Request, call_next):
        # Read header or query param for active experiment ID
        exp_id = request.headers.get("x-experiment-id") or request.query_params.get("experiment_id")
        if exp_id:
            req_id = request.headers.get("x-request-id", str(uuid.uuid4()))
            variant = self.experiment_manager.select_variant_for_request(exp_id, req_id)
            if variant:
                request.state.experiment_id = exp_id
                request.state.experiment_variant = variant

        response = await call_next(request)
        if hasattr(request.state, "experiment_variant"):
            response.headers["x-experiment-variant"] = request.state.experiment_variant.variant_id
        return response
