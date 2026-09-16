from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import get_settings
from app.limits.exceptions import QuotaExceededException, RateLimitExceededException
from app.limits.quota_service import QuotaService
from app.limits.rate_limit_service import RateLimitService


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate_limit_service: RateLimitService, quota_service: QuotaService):
        super().__init__(app)
        self.rate_limit_service = rate_limit_service
        self.quota_service = quota_service
        self.settings = get_settings()

    async def dispatch(self, request: Request, call_next):
        if not self.settings.rate_limiting_enabled:
            return await call_next(request)

        # Skip rate limits for non-api routes like docs/health
        if not request.url.path.startswith(self.settings.api_prefix):
            return await call_next(request)

        # Extract context populated by TenantMiddleware and AuthenticationMiddleware
        org_id = getattr(request.state, "organization_id", None)
        workspace_id = getattr(request.state, "workspace_id", None)
        api_key_id = getattr(request.state, "api_key_id", None)
        user_id = getattr(request.state, "user_id", None)

        # Only rate limit authenticated requests.
        # Anonymous limits can be handled via IP if needed, but not in this scope.
        if not org_id:
            return await call_next(request)

        # 1. Evaluate Quotas
        try:
            await self.quota_service.evaluate_quotas(
                organization_id=org_id,
                workspace_id=workspace_id,
                api_key_id=api_key_id,
                user_id=user_id
            )
        except QuotaExceededException as e:
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
        except Exception as e:
            # Failsafe open for unhandled db errors in quota
            import logging
            logging.getLogger(__name__).error(f"Quota check error: {e}")

        # 2. Evaluate Rate Limits
        limit = self.settings.default_requests_per_minute
        window = 60

        # In a full implementation, RateLimitService would fetch the specific RateLimitPolicy
        # For this walkthrough, we apply the default limit to the org
        try:
            await self.rate_limit_service.check_rate_limit(
                scope_id=f"org:{org_id}",
                limit=limit,
                window_seconds=window
            )
        except RateLimitExceededException as e:
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

        # 3. Acquire Concurrency Lease
        lease_id = None
        try:
            lease_id = await self.rate_limit_service.acquire_concurrency_lease(
                scope_id=f"org:{org_id}",
                limit=self.settings.default_concurrent_requests,
                ttl_seconds=120
            )
        except RateLimitExceededException as e:
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

        # Proceed with execution
        try:
            response = await call_next(request)
            return response
        finally:
            if lease_id:
                await self.rate_limit_service.release_concurrency_lease(
                    scope_id=f"org:{org_id}",
                    lease_id=lease_id
                )
