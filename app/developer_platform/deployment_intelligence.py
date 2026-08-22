"""Deployment Telemetry Regression & Rollback Recommendation Subsystem."""

from datetime import datetime, timezone
import uuid
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.approvals.approval_engine import ApprovalEngine

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class RollbackRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:10]}")
    release_id: str
    risk_level: str = "HIGH"
    approval_request_id: Optional[str] = None
    reason: str = ""
    created_at: datetime = Field(default_factory=_now)


class DeploymentIntelligenceEngine:
    """Detects telemetry regressions and generates rollback recommendations gated by ApprovalEngine."""

    def __init__(self, approval_engine: Optional[ApprovalEngine] = None) -> None:
        self.approval_engine = approval_engine or ApprovalEngine()

    def evaluate_deployment_health(self, release_id: str, error_rate_pct: float, tenant_id: str = "global") -> Optional[RollbackRecommendation]:
        if error_rate_pct > 5.0:
            appr = self.approval_engine.request_approval(
                execution_id=f"rollback_{release_id}",
                action_type="ROLLBACK_RELEASE",
                tenant_id=tenant_id,
            )
            rec = RollbackRecommendation(
                release_id=release_id,
                risk_level="HIGH",
                approval_request_id=appr.request_id,
                reason=f"High error rate ({error_rate_pct}%) detected post-deployment",
            )
            logger.warning(f"[DEPLOYMENT INTELLIGENCE] High error rate post-deployment! Rollback recommendation generated -> Approval '{appr.request_id}'")
            return rec
        return None
