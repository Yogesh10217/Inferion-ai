from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.billing.budget_service import BudgetService
from app.billing.exceptions import BudgetExceededException
from app.core.logger import get_logger

logger = get_logger(__name__)


class BudgetMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, budget_service: BudgetService):
        super().__init__(app)
        self.budget_service = budget_service

    async def dispatch(self, request: Request, call_next):

        # Only apply to execution endpoints
        if not request.url.path.startswith("/v1/chat/") and not request.url.path.startswith("/v1/models"):
            return await call_next(request)

        org_id = getattr(request.state, "organization_id", None)
        if not org_id:
            return await call_next(request)

        workspace_id = getattr(request.state, "workspace_id", None)

        try:
            # Check budgets in O(1) cache. If exceeded, throws BudgetExceededException
            await self.budget_service.check_budget_limit(org_id, workspace_id)
            if workspace_id:
                await self.budget_service.check_budget_limit(org_id, None)

        except BudgetExceededException as e:
            logger.warning(f"Budget hard limit exceeded for org_id={org_id}, workspace_id={workspace_id}")
            return JSONResponse(status_code=e.status_code, content={"error": "payment_required", "message": e.detail})

        response = await call_next(request)
        return response
