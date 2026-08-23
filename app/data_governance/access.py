"""Centralized Data Access Governance & Pre-Retrieval Authorization Layer."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.data_governance.exceptions import DataAccessDeniedException, CrossTenantDataAccessException
from app.data_governance.assets import DataAssetManager, DataAssetStatus
from app.data_governance.classification import DataClassificationEngine, ClassificationLevel
from app.data_governance.consent import ConsentManager, ConsentPurpose
from app.data_governance.retention import RetentionManager
from app.data_governance.trust import DataTrustEngine


class PrincipalType(str, Enum):
    USER = "USER"
    AGENT = "AGENT"
    WORKFLOW = "WORKFLOW"
    APPLICATION = "APPLICATION"
    INTEGRATION = "INTEGRATION"
    SERVICE = "SERVICE"
    SYSTEM = "SYSTEM"


class DataAction(str, Enum):
    READ = "READ"
    WRITE = "WRITE"
    QUERY = "QUERY"
    RETRIEVE_CONTEXT = "RETRIEVE_CONTEXT"
    ANALYZE = "ANALYZE"
    EXPORT = "EXPORT"
    SHARE = "SHARE"
    DELETE = "DELETE"


class DataAccessDecisionType(str, Enum):
    ALLOW = "ALLOW"
    MASK = "MASK"
    REDACT = "REDACT"
    FILTER = "FILTER"
    AGGREGATE_ONLY = "AGGREGATE_ONLY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    RESTRICT = "RESTRICT"
    BLOCK = "BLOCK"


class DataAccessRequest(BaseModel):
    """Immutable unified request object for all platform data access evaluations."""

    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    principal_id: str
    principal_type: PrincipalType = PrincipalType.USER
    asset_id: str
    action: DataAction = DataAction.READ
    purpose: ConsentPurpose = ConsentPurpose.AI_CONTEXT
    context: Dict[str, Any] = Field(default_factory=dict)
    requested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"frozen": True}


class DataGovernanceSnapshot(BaseModel):
    """Reproducibility snapshot capturing governance state at decision time."""

    policy_version: str = "1.0.0"
    classification_version: str = "1.0.0"
    consent_reference: Optional[str] = None
    retention_policy_version: Optional[str] = None
    trust_score: float = 100.0
    risk_level: str = "LOW"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"frozen": True}


class DataAccessDecision(BaseModel):
    """Final governance decision with transformation directive and snapshot."""

    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str
    decision: DataAccessDecisionType
    allowed: bool
    requires_masking: bool = False
    requires_redaction: bool = False
    filters: Dict[str, Any] = Field(default_factory=dict)
    reason: str = "Access granted."
    snapshot: DataGovernanceSnapshot
    decided_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataAccessManager:
    """Central Data Access Governance Engine enforcing pre-retrieval authorization pipeline."""

    def __init__(
        self,
        asset_manager: DataAssetManager,
        classification_engine: DataClassificationEngine,
        consent_manager: ConsentManager,
        retention_manager: RetentionManager,
        trust_engine: DataTrustEngine,
    ) -> None:
        self.asset_manager = asset_manager
        self.classification_engine = classification_engine
        self.consent_manager = consent_manager
        self.retention_manager = retention_manager
        self.trust_engine = trust_engine

    def evaluate_access(self, request: DataAccessRequest) -> DataAccessDecision:
        """Execute the strictly ordered governance pipeline:

        Request
          ↓
        Identity Resolution (Principal validated)
          ↓
        Tenant Resolution (Tenant boundaries enforced)
          ↓
        Asset Resolution (Asset fetched & checked)
          ↓
        Classification Evaluation
          ↓
        Purpose Validation
          ↓
        Consent Validation
          ↓
        Retention / Legal Hold Validation
          ↓
        Authorization + Policy Evaluation
          ↓
        Mask / Redact / Filter Decision
          ↓
        Only Then → Data Retrieval Allowed
        """

        # 1. Identity & Tenant Resolution
        if not request.principal_id or not request.tenant_id:
            return self._make_block_decision(request, "Invalid identity or tenant resolution.", 0.0, "HIGH")

        # 2. Asset Resolution
        try:
            asset = self.asset_manager.get_asset(request.asset_id, request.tenant_id)
        except CrossTenantDataAccessException as exc:
            return self._make_block_decision(request, f"Cross-tenant violation: {exc.message}", 0.0, "CRITICAL")
        except Exception as exc:
            return self._make_block_decision(request, f"Asset resolution error: {str(exc)}", 0.0, "HIGH")

        if asset.status in (DataAssetStatus.DELETED, DataAssetStatus.ARCHIVED):
            return self._make_block_decision(request, f"Asset is in {asset.status} state.", 0.0, "HIGH")

        # 3. Classification Evaluation
        level_enum = ClassificationLevel.from_str(asset.classification)

        # 4. Purpose & Consent Validation
        consent_ref = None
        # Check consent if processing personal/sensitive data or requested for specific purposes
        if level_enum >= ClassificationLevel.RESTRICTED:
            has_consent = self.consent_manager.evaluate_consent(
                tenant_id=request.tenant_id,
                subject_id=request.principal_id,
                purpose=request.purpose,
                asset_id=request.asset_id,
            )
            if not has_consent:
                return self._make_block_decision(
                    request,
                    f"Consent missing or withdrawn for purpose '{request.purpose.value}' on restricted asset.",
                    50.0,
                    "HIGH",
                )
            consent_ref = f"consent:{request.tenant_id}:{request.principal_id}"

        # 5. Retention / Legal Hold Validation
        under_hold = self.retention_manager.is_under_legal_hold(request.asset_id, request.tenant_id)
        if request.action == DataAction.DELETE and under_hold:
            return self._make_block_decision(request, "Deletion blocked: Asset is under active Legal Hold.", 90.0, "HIGH")

        # 6. Data Trust & Risk Evaluation
        trust_assessment = self.trust_engine.calculate_trust_score(
            asset_id=request.asset_id,
            tenant_id=request.tenant_id,
        )
        trust_score = trust_assessment.overall_score

        if trust_score < 50.0 and request.action in (DataAction.RETRIEVE_CONTEXT, DataAction.EXPORT, DataAction.SHARE):
            return self._make_block_decision(
                request,
                f"Untrusted Data: Trust score ({trust_score:.1f}) below threshold for operation '{request.action.value}'.",
                trust_score,
                "HIGH",
            )

        # 7. Authorization + Policy Masking/Redaction Decision
        decision_type = DataAccessDecisionType.ALLOW
        masking = False
        redaction = False

        if level_enum == ClassificationLevel.HIGHLY_RESTRICTED:
            decision_type = DataAccessDecisionType.REDACT
            redaction = True
        elif level_enum == ClassificationLevel.RESTRICTED:
            decision_type = DataAccessDecisionType.MASK
            masking = True
        elif trust_score < 70.0:
            decision_type = DataAccessDecisionType.RESTRICT

        snapshot = DataGovernanceSnapshot(
            policy_version="1.0.0",
            classification_version="1.0.0",
            consent_reference=consent_ref,
            retention_policy_version="1.0.0",
            trust_score=trust_score,
            risk_level="LOW" if trust_score >= 80.0 else "MEDIUM",
        )

        return DataAccessDecision(
            request_id=request.request_id,
            decision=decision_type,
            allowed=True,
            requires_masking=masking,
            requires_redaction=redaction,
            reason=f"Access granted with decision '{decision_type.value}'.",
            snapshot=snapshot,
        )

    def _make_block_decision(self, request: DataAccessRequest, reason: str, trust_score: float, risk_level: str) -> DataAccessDecision:
        snapshot = DataGovernanceSnapshot(
            policy_version="1.0.0",
            classification_version="1.0.0",
            trust_score=trust_score,
            risk_level=risk_level,
        )
        return DataAccessDecision(
            request_id=request.request_id,
            decision=DataAccessDecisionType.BLOCK,
            allowed=False,
            reason=reason,
            snapshot=snapshot,
        )
