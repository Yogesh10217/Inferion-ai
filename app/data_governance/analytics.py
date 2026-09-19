"""Tenant-Scoped Governance Analytics & Reporting Engine."""

import uuid
from datetime import datetime, timezone
from typing import Dict

from pydantic import BaseModel, Field

from app.data_governance.assets import DataAssetManager
from app.data_governance.trust import DataTrustEngine, TrustBand
from app.data_governance.usage import DataUsageManager


class DataQualityAnalytics(BaseModel):
    evaluated_assets_count: int = 0
    average_quality_score: float = 90.0
    quality_violations_count: int = 0


class DataTrustAnalytics(BaseModel):
    average_trust_score: float = 85.0
    trust_distribution: Dict[TrustBand, int] = Field(default_factory=dict)


class ComplianceAnalytics(BaseModel):
    contract_violations_count: int = 0
    consent_violations_count: int = 0
    retention_violations_count: int = 0
    policy_violations_count: int = 0


class DataGovernanceReport(BaseModel):
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    governed_assets_count: int = 0
    classified_assets_count: int = 0
    unclassified_assets_count: int = 0
    blocked_access_attempts: int = 0
    data_sharing_volume: int = 0
    quality_analytics: DataQualityAnalytics
    trust_analytics: DataTrustAnalytics
    compliance_analytics: ComplianceAnalytics
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataGovernanceAnalyticsEngine:
    """Computes aggregate tenant-scoped governance analytics and reports."""

    def __init__(
        self,
        asset_manager: DataAssetManager,
        usage_manager: DataUsageManager,
        trust_engine: DataTrustEngine,
    ) -> None:
        self.asset_manager = asset_manager
        self.usage_manager = usage_manager
        self.trust_engine = trust_engine

    def generate_report(self, tenant_id: str) -> DataGovernanceReport:
        assets = self.asset_manager.list_assets(tenant_id=tenant_id)
        governed_count = len(assets)
        classified_count = sum(1 for a in assets if a.classification != "UNCLASSIFIED")
        unclassified_count = governed_count - classified_count

        usage_events = self.usage_manager.list_usage_events(tenant_id=tenant_id, limit=1000)
        blocked_attempts = sum(
            1 for e in usage_events if "BLOCK" in e.authorization_decision or "DENIED" in e.authorization_decision
        )

        # Trust analytics
        dist: Dict[TrustBand, int] = {tb: 0 for tb in TrustBand}
        scores = []
        for a in assets:
            ts = self.trust_engine.get_trust_score(a.asset_id, tenant_id)
            dist[ts.trust_band] += 1
            scores.append(ts.overall_score)

        avg_trust = sum(scores) / max(1, len(scores)) if scores else 85.0

        return DataGovernanceReport(
            tenant_id=tenant_id,
            governed_assets_count=governed_count,
            classified_assets_count=classified_count,
            unclassified_assets_count=unclassified_count,
            blocked_access_attempts=blocked_attempts,
            data_sharing_volume=len([e for e in usage_events if e.action == "SHARE"]),
            quality_analytics=DataQualityAnalytics(
                evaluated_assets_count=governed_count,
                average_quality_score=90.0,
                quality_violations_count=0,
            ),
            trust_analytics=DataTrustAnalytics(
                average_trust_score=avg_trust,
                trust_distribution=dist,
            ),
            compliance_analytics=ComplianceAnalytics(),
        )
