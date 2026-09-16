"""Marketplace Review Pipeline & Governance Engine."""

import logging
from typing import Optional

from pydantic import BaseModel

from app.approvals.approval_engine import ApprovalEngine
from app.approvals.approval_policies import RiskLevel
from app.extensions.security import ExtensionSecurityEngine, SecurityAnalysisReport
from app.marketplace.marketplace_item import ItemLifecycle, MarketplaceItem

logger = logging.getLogger(__name__)


class ReviewResult(BaseModel):
    """Structured result output of a marketplace review pipeline."""

    item_id: str
    security_report: SecurityAnalysisReport
    approval_required: bool = False
    approval_request_id: Optional[str] = None
    passed_review: bool = True
    comments: str = "Manifest and security analysis clean"


class MarketplaceReviewEngine:
    """Automates review pipeline for marketplace item submissions."""

    def __init__(
        self,
        security_engine: Optional[ExtensionSecurityEngine] = None,
        approval_engine: Optional[ApprovalEngine] = None,
    ) -> None:
        self.security_engine = security_engine or ExtensionSecurityEngine()
        self.approval_engine = approval_engine or ApprovalEngine()

    def review_item_submission(self, item: MarketplaceItem, publisher_verified: bool = True) -> ReviewResult:
        """Execute automated review pipeline: Manifest -> Integrity -> Permissions -> Risk -> Approvals."""
        item.status = ItemLifecycle.UNDER_REVIEW
        sec_report = self.security_engine.analyze_extension_security(item.manifest, publisher_verified=publisher_verified)

        appr_req_id = None
        if sec_report.requires_approval:
            req = self.approval_engine.request_approval(
                execution_id=item.item_id,
                action_type="marketplace_item_publish",
                risk_level=RiskLevel.HIGH,
                requester=item.publisher_id,
                payload={"title": item.title, "risk_score": sec_report.risk_score},
            )
            appr_req_id = req.request_id
            logger.warning(f"[MARKETPLACE REVIEW] Item '{item.title}' requires approval (ID: {appr_req_id})")

        passed = sec_report.risk_score < 8.0
        if passed and not sec_report.requires_approval:
            item.status = ItemLifecycle.APPROVED
        elif not passed:
            item.status = ItemLifecycle.REJECTED

        return ReviewResult(
            item_id=item.item_id,
            security_report=sec_report,
            approval_required=sec_report.requires_approval,
            approval_request_id=appr_req_id,
            passed_review=passed,
            comments="Passed automated security scan" if passed else "High risk score detected",
        )
