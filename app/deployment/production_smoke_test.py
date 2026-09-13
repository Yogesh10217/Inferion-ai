from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.deployment.models import PlatformReadinessClassification
from app.deployment.secrets import SecretsSanitizer


@dataclass
class SmokeTestCase:
    test_id: str
    target_endpoint: str
    expected_status_code: int
    validation_type: str
    description: str


@dataclass
class ProductionSmokeTestPlan:
    plan_name: str = "Canonical Production Smoke Test Suite"
    target_url: str = "http://127.0.0.1:8003"  # Simulation default, NEVER auto-production
    target_environment: str = "PRODUCTION_SIMULATION"
    test_cases: List[SmokeTestCase] = field(
        default_factory=lambda: [
            SmokeTestCase("ST-01", "/live", 200, "HTTP_GET", "Verify application liveness probe"),
            SmokeTestCase("ST-02", "/ready", 200, "HTTP_GET", "Verify application readiness probe"),
            SmokeTestCase("ST-03", "/health", 200, "HTTP_GET", "Verify application health and dependency status"),
            SmokeTestCase("ST-04", "/health", 200, "HEADERS", "Verify security headers (HSTS, NoSniff, CSP)"),
            SmokeTestCase("ST-05", "/docs", 404, "HTTP_GET", "Verify OpenAPI documentation protection in production mode"),
            SmokeTestCase("ST-06", "/redoc", 404, "HTTP_GET", "Verify ReDoc documentation protection in production mode"),
            SmokeTestCase("ST-07", "/openapi.json", 404, "HTTP_GET", "Verify OpenAPI JSON spec protection in production mode"),
            SmokeTestCase("ST-08", "/health", 200, "MANAGERS", "Verify 9 Intelligence Managers registered in ServiceContainer"),
        ]
    )
    execution_status: str = "PRODUCTION_SMOKE_TEST_NOT_EXECUTED"

    def sanitized_dict(self) -> Dict[str, Any]:
        return SecretsSanitizer.sanitize_structure({
            "plan_name": self.plan_name,
            "target_url": self.target_url,
            "target_environment": self.target_environment,
            "test_cases_count": len(self.test_cases),
            "execution_status": self.execution_status,
        })


@dataclass
class SmokeTestExecutionResult:
    plan: ProductionSmokeTestPlan
    passed: bool
    passed_count: int
    failed_count: int
    execution_status: str
    executed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ProductionSmokeTestPlanEvaluator:
    """Evaluates and prepares production smoke test plans with target safety enforcement."""

    @classmethod
    def evaluate_smoke_test_plan(
        cls, target_url: str = "http://127.0.0.1:8003", target_environment: str = "PRODUCTION_SIMULATION"
    ) -> ProductionSmokeTestPlan:
        # Enforce target safety: Never auto-target live production domain without explicit override
        if "api.production-domain.com" in target_url:
            exec_status = "PRODUCTION_SMOKE_TEST_NOT_EXECUTED"
        else:
            exec_status = "SMOKE_TEST_PLAN_READY"

        return ProductionSmokeTestPlan(
            target_url=target_url,
            target_environment=target_environment,
            execution_status=exec_status,
        )
