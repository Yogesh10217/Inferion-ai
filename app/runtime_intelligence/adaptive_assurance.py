"""Adaptive assurance engine for Runtime Intelligence (Phase 5.57)."""

import logging
from typing import Dict, Any, Optional
from app.runtime_intelligence.models import AdaptiveAssuranceScore

logger = logging.getLogger(__name__)


class AdaptiveAssuranceEngine:
    """Synthesizes holistic runtime assurance score across health, risk, trust, resilience, and evidence."""

    def evaluate_assurance(
        self,
        tenant_id: str,
        health_score: float = 0.95,
        risk_score: Optional[float] = None,
        resilience_score: Optional[float] = None,
        evidence_integrity_score: float = 0.99,
        security_score: float = 0.96,
    ) -> AdaptiveAssuranceScore:
        # Convert risk score into assurance component (lower risk -> higher assurance)
        computed_risk_component = 1.0 - (risk_score if risk_score is not None else 0.15)
        computed_resilience = resilience_score if resilience_score is not None else 0.92

        comp_scores = {
            "health": round(health_score, 3),
            "risk": round(computed_risk_component, 3),
            "trust": round((health_score + computed_risk_component) / 2.0, 3),
            "security": round(security_score, 3),
            "policy": 0.98,
            "resilience": round(computed_resilience, 3),
            "evidence": round(evidence_integrity_score, 3),
        }
        overall = sum(comp_scores.values()) / len(comp_scores)

        if overall >= 0.90:
            posture = "ASSURED"
        elif overall >= 0.75:
            posture = "WATCH"
        elif overall >= 0.60:
            posture = "DEGRADED"
        elif overall >= 0.40:
            posture = "AT_RISK"
        else:
            posture = "CRITICAL"

        score = AdaptiveAssuranceScore(
            tenant_id=tenant_id,
            assurance_score=round(overall, 4),
            posture=posture,
            component_scores=comp_scores,
        )
        logger.info(f"Evaluated AdaptiveAssuranceScore for tenant '{tenant_id}': Score={overall:.4f}, Posture={posture}")
        return score
