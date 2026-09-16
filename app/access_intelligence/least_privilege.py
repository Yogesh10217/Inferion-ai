"""Least Privilege Intelligence (Phase 5.39)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.access_intelligence.exceptions import CrossTenantAccessIntelligenceException


class PrivilegeSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class PrivilegeGap(BaseModel):
    """Identified privilege gap / excess entitlement."""
    gap_id: str = Field(default_factory=lambda: f"gap_{uuid.uuid4().hex[:8]}")
    identity_id: str
    entitlement_id: str
    gap_type: str  # EXCESSIVE_PERMISSIONS, UNUSED_PERMISSIONS, OVERLY_BROAD_ROLE, PRIVILEGE_ACCUMULATION, UNNECESSARY_PROD_ACCESS
    severity: PrivilegeSeverity
    description: str
    days_unused: int = 0


class PrivilegeRecommendation(BaseModel):
    """Non-mutating recommendation for privilege reduction."""
    recommendation_id: str = Field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:8]}")
    gap_id: str
    action_type: str  # REVOKE_ENTITLEMENT, REDUCE_SCOPE, SPLIT_ROLE, EXPIRE_ACCESS
    recommended_entitlement_id: str
    reason: str
    impact_score: float = 0.0


class LeastPrivilegeAssessment(BaseModel):
    """Least Privilege Assessment Result."""
    assessment_id: str = Field(default_factory=lambda: f"lp_eval_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_identity_id: str
    total_entitlements_count: int = 0
    unused_entitlements_count: int = 0
    overly_broad_count: int = 0
    privilege_score: float = 100.0  # 100 = perfectly least-privileged, lower = over-privileged
    gaps: List[PrivilegeGap] = Field(default_factory=list)
    recommendations: List[PrivilegeRecommendation] = Field(default_factory=list)
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LeastPrivilegeManager:
    """Least Privilege Intelligence Manager."""

    def __init__(self) -> None:
        self._assessments: Dict[str, LeastPrivilegeAssessment] = {}

    def assess_identity(
        self,
        tenant_id: str,
        identity_id: str,
        assigned_entitlement_ids: List[str],
        used_entitlement_ids: List[str],
        is_production_access: bool = False,
    ) -> LeastPrivilegeAssessment:
        gaps: List[PrivilegeGap] = []
        recs: List[PrivilegeRecommendation] = []

        unused = [e for e in assigned_entitlement_ids if e not in used_entitlement_ids]
        for ent_id in unused:
            gap = PrivilegeGap(
                identity_id=identity_id,
                entitlement_id=ent_id,
                gap_type="UNUSED_PERMISSIONS",
                severity=PrivilegeSeverity.HIGH if is_production_access else PrivilegeSeverity.MEDIUM,
                description=f"Entitlement '{ent_id}' assigned to identity '{identity_id}' has not been used.",
                days_unused=90,
            )
            gaps.append(gap)
            rec = PrivilegeRecommendation(
                gap_id=gap.gap_id,
                action_type="REVOKE_ENTITLEMENT",
                recommended_entitlement_id=ent_id,
                reason=f"Revoke unused entitlement '{ent_id}' to maintain least privilege posture.",
            )
            recs.append(rec)

        if len(assigned_entitlement_ids) > 10:
            gap = PrivilegeGap(
                identity_id=identity_id,
                entitlement_id="ALL",
                gap_type="PRIVILEGE_ACCUMULATION",
                severity=PrivilegeSeverity.HIGH,
                description=f"Identity '{identity_id}' exhibits privilege accumulation ({len(assigned_entitlement_ids)} entitlements).",
            )
            gaps.append(gap)

        total_cnt = len(assigned_entitlement_ids)
        unused_cnt = len(unused)
        priv_score = max(0.0, 100.0 - (unused_cnt * 15.0) - (10.0 if len(assigned_entitlement_ids) > 10 else 0.0))

        asm = LeastPrivilegeAssessment(
            tenant_id=tenant_id,
            target_identity_id=identity_id,
            total_entitlements_count=total_cnt,
            unused_entitlements_count=unused_cnt,
            overly_broad_count=len(gaps),
            privilege_score=priv_score,
            gaps=gaps,
            recommendations=recs,
        )
        self._assessments[asm.assessment_id] = asm
        return asm

    def get_assessment(self, tenant_id: str, assessment_id: str) -> LeastPrivilegeAssessment:
        asm = self._assessments.get(assessment_id)
        if not asm or asm.tenant_id != tenant_id:
            raise CrossTenantAccessIntelligenceException()
        return asm
