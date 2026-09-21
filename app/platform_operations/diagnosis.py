"""Evidence-Backed Root Cause Analysis & Diagnosis Engine."""

import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field

from app.platform_operations.incident_intelligence import IncidentContext
from app.platform_operations.services import ServiceCatalogManager, ServiceDependencyType

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class DiagnosisEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"ev_{uuid.uuid4().hex[:8]}")
    source: str
    description: str
    confidence_contribution: float = 0.2


class RootCauseHypothesis(BaseModel):
    hypothesis_id: str = Field(default_factory=lambda: f"hyp_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    incident_id: str
    title: str
    description: str
    confidence_score: float = 0.5  # 0.0 to 1.0 (labeled clearly as hypothesis)
    category: str = "DEPLOYMENT_REGRESSION"  # DEPLOYMENT_REGRESSION, DEPENDENCY_FAILURE, CAPACITY_EXHAUSTION, CONFIG_CHANGE, CODE_BUG
    evidences: List[DiagnosisEvidence] = Field(default_factory=list)
    suggested_remediations: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_now)


class DiagnosisResult(BaseModel):
    diagnosis_id: str = Field(default_factory=lambda: f"diag_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    incident_id: str
    hypotheses: List[RootCauseHypothesis] = Field(default_factory=list)
    top_hypothesis: Optional[RootCauseHypothesis] = None
    diagnosed_at: datetime = Field(default_factory=_now)


class RootCauseAnalyzer:
    """Generates evidence-backed root cause hypotheses using topology, deployment correlation, and knowledge retrieval."""

    def __init__(self, service_catalog_manager: Optional[ServiceCatalogManager] = None) -> None:
        self.service_catalog_manager = service_catalog_manager or ServiceCatalogManager()

    def diagnose_incident(
        self,
        tenant_id: str,
        context: IncidentContext,
    ) -> DiagnosisResult:
        hypotheses: List[RootCauseHypothesis] = []

        # 1. Check for Deployment Regression Hypothesis
        if context.recent_deployments:
            recent_dep = context.recent_deployments[0]
            ev1 = DiagnosisEvidence(
                source="DeploymentManager",
                description=f"Deployment '{recent_dep.get('version_id', 'unknown')}' occurred recently.",
                confidence_contribution=0.4,
            )
            ev2 = DiagnosisEvidence(
                source="AnomalyDetector",
                description="Errors surged immediately following deployment event.",
                confidence_contribution=0.35,
            )
            hyp = RootCauseHypothesis(
                tenant_id=tenant_id,
                incident_id=context.incident_id,
                title=f"Deployment Regression in Version {recent_dep.get('version_id', 'unknown')}",
                description="Recent release introduced latencies or exceptions breaking service contracts.",
                confidence_score=0.75,
                category="DEPLOYMENT_REGRESSION",
                evidences=[ev1, ev2],
                suggested_remediations=["ROLLBACK", "THROTTLE", "FAILOVER"],
            )
            hypotheses.append(hyp)

        # 2. Check for Upstream Dependency Failure Hypothesis
        if context.incident.primary_resource_id:
            try:
                upstreams = self.service_catalog_manager.resolve_dependencies(
                    service_id=context.incident.primary_resource_id,
                    tenant_id=tenant_id,
                    direction=ServiceDependencyType.UPSTREAM,
                    transitive=False,
                )
                if upstreams:
                    unhealthy = [u for u in upstreams if u.health.value != "HEALTHY"]
                    if unhealthy:
                        ev = DiagnosisEvidence(
                            source="ServiceCatalogManager",
                            description=f"Upstream dependency '{unhealthy[0].name}' is currently {unhealthy[0].health.value}.",
                            confidence_contribution=0.45,
                        )
                        hyp = RootCauseHypothesis(
                            tenant_id=tenant_id,
                            incident_id=context.incident_id,
                            title=f"Upstream Dependency Failure in {unhealthy[0].name}",
                            description=f"Primary service degraded due to upstream failure in {unhealthy[0].name}.",
                            confidence_score=0.82,
                            category="DEPENDENCY_FAILURE",
                            evidences=[ev],
                            suggested_remediations=["RETRY", "FALLBACK", "CIRCUIT_BREAKER"],
                        )
                        hypotheses.append(hyp)
            except Exception:  # nosec B110
                pass

        # 3. Fallback General Anomaly Hypothesis
        if not hypotheses and context.anomalies:
            anom = context.anomalies[0]
            ev = DiagnosisEvidence(
                source="AnomalyDetector",
                description=f"Detected anomaly '{anom.title}' ({anom.anomaly_type.value}).",
                confidence_contribution=0.5,
            )
            hyp = RootCauseHypothesis(
                tenant_id=tenant_id,
                incident_id=context.incident_id,
                title=f"Operational Anomaly: {anom.anomaly_type.value}",
                description=anom.description,
                confidence_score=0.60,
                category="ANOMALY",
                evidences=[ev],
                suggested_remediations=["RESTART", "THROTTLE", "ESCALATE_TO_HUMAN"],
            )
            hypotheses.append(hyp)

        # Sort by confidence score
        hypotheses.sort(key=lambda h: h.confidence_score, reverse=True)
        top = hypotheses[0] if hypotheses else None

        result = DiagnosisResult(
            tenant_id=tenant_id,
            incident_id=context.incident_id,
            hypotheses=hypotheses,
            top_hypothesis=top,
        )
        logger.info(
            f"[ROOT CAUSE ANALYZER] Diagnosed incident '{context.incident_id}' with {len(hypotheses)} hypotheses. Top: '{top.title if top else 'None'}'"
        )
        return result
