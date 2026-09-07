"""
Unified Impact Analysis Engine for Phase 5.51 Enterprise AI Unified Intelligence.

Evaluates cross-domain impact across business, security, identity, operations,
compliance, data, and model assets with tenant isolation.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from app.unified_intelligence.exceptions import (
    CrossTenantUnifiedIntelligenceException,
    InvalidUnifiedIntelligenceInputException
)
from app.unified_intelligence.domains import IntelligenceDomain
from app.unified_intelligence.situation_awareness import EnterpriseSituation, SituationSeverity


class UnifiedImpactAssessment:
    """
    Cross-domain impact assessment result for an enterprise situation or set of signals.
    """
    def __init__(
        self,
        impact_id: str,
        tenant_id: str,
        situation_id: str,
        business_impact_score: float,
        security_impact_score: float,
        operational_impact_score: float,
        compliance_impact_score: float,
        aggregate_impact_score: float,
        affected_domains: List[IntelligenceDomain],
        affected_entities: List[str],
        impact_summary: str,
        confidence_score: float,
        created_at: Optional[datetime] = None
    ):
        self.impact_id = impact_id
        self.tenant_id = tenant_id
        self.situation_id = situation_id
        self.business_impact_score = min(max(business_impact_score, 0.0), 1.0)
        self.security_impact_score = min(max(security_impact_score, 0.0), 1.0)
        self.operational_impact_score = min(max(operational_impact_score, 0.0), 1.0)
        self.compliance_impact_score = min(max(compliance_impact_score, 0.0), 1.0)
        self.aggregate_impact_score = min(max(aggregate_impact_score, 0.0), 1.0)
        self.affected_domains = affected_domains
        self.affected_entities = affected_entities
        self.impact_summary = impact_summary
        self.confidence_score = min(max(confidence_score, 0.0), 1.0)
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "impact_id": self.impact_id,
            "tenant_id": self.tenant_id,
            "situation_id": self.situation_id,
            "business_impact_score": round(self.business_impact_score, 4),
            "security_impact_score": round(self.security_impact_score, 4),
            "operational_impact_score": round(self.operational_impact_score, 4),
            "compliance_impact_score": round(self.compliance_impact_score, 4),
            "aggregate_impact_score": round(self.aggregate_impact_score, 4),
            "affected_domains": [d.value for d in self.affected_domains],
            "affected_entities": self.affected_entities,
            "impact_summary": self.impact_summary,
            "confidence_score": round(self.confidence_score, 4),
            "created_at": self.created_at.isoformat()
        }


class UnifiedImpactEngine:
    """
    Engine to evaluate cross-domain impact for unified intelligence situations and risk propagation.
    """
    def __init__(self):
        pass

    def evaluate_situation_impact(
        self,
        tenant_id: str,
        situation: EnterpriseSituation
    ) -> UnifiedImpactAssessment:
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")
        if situation.tenant_id != tenant_id:
            raise CrossTenantUnifiedIntelligenceException(
                f"Tenant mismatch in impact evaluation: requested {tenant_id}, situation has {situation.tenant_id}"
            )

        # Severity weights
        severity_multipliers = {
            SituationSeverity.LOW: 0.2,
            SituationSeverity.MEDIUM: 0.5,
            SituationSeverity.HIGH: 0.75,
            SituationSeverity.CRITICAL: 1.0
        }
        mult = severity_multipliers.get(situation.severity, 0.5)

        # Calculate scores based on domain distribution
        domain_set = set(situation.participating_domains)
        sec_score = 0.8 * mult if IntelligenceDomain.SECURITY in domain_set else 0.2 * mult
        ops_score = 0.8 * mult if IntelligenceDomain.OPERATIONS in domain_set else 0.2 * mult
        comp_score = 0.8 * mult if IntelligenceDomain.POLICY in domain_set else 0.2 * mult
        biz_score = max(sec_score, ops_score, comp_score) * 0.9

        agg_score = (sec_score * 0.3) + (ops_score * 0.3) + (comp_score * 0.2) + (biz_score * 0.2)
        confidence = situation.confidence_score * 0.95

        impact_id = f"imp-{uuid.uuid4().hex[:12]}"
        summary = (
            f"Impact assessment for situation {situation.title}: aggregate impact score {agg_score:.2f} "
            f"across {len(domain_set)} domains ({len(situation.affected_entities)} affected entities)."
        )

        return UnifiedImpactAssessment(
            impact_id=impact_id,
            tenant_id=tenant_id,
            situation_id=situation.situation_id,
            business_impact_score=biz_score,
            security_impact_score=sec_score,
            operational_impact_score=ops_score,
            compliance_impact_score=comp_score,
            aggregate_impact_score=agg_score,
            affected_domains=list(domain_set),
            affected_entities=situation.affected_entities,
            impact_summary=summary,
            confidence_score=confidence
        )
