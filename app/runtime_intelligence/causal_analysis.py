"""Explainable causal hypothesis engine for Runtime Intelligence (Phase 5.57)."""

import logging
from typing import List, Optional

from app.runtime_intelligence.models import RuntimeCausalHypothesis

logger = logging.getLogger(__name__)


class RuntimeCausalAnalysisEngine:
    """Builds explainable causal hypotheses with evidence pointers and confidence scores."""

    def analyze_causal_hypothesis(
        self,
        tenant_id: str,
        hypothesis_statement: str,
        evidence_ids: List[str],
        affected_subsystems: Optional[List[str]] = None,
    ) -> RuntimeCausalHypothesis:
        evidence_count = len(evidence_ids)
        subsystems = affected_subsystems or ["upstream_service"]

        if evidence_count >= 3:
            status = "CONFIRMED"
            confidence = 0.94
            notes = f"Strong multi-source corroboration ({evidence_count} evidence items) indicates {hypothesis_statement.lower()} propagating to {', '.join(subsystems)}."
        elif evidence_count >= 1:
            status = "SUPPORTED"
            confidence = 0.85
            notes = f"Direct evidence pointer ({evidence_ids[0]}) supports causal linkage: {hypothesis_statement} impacting {', '.join(subsystems)}."
        else:
            status = "HYPOTHESIZED"
            confidence = 0.60
            notes = f"Working hypothesis requiring additional telemetry: {hypothesis_statement} for {', '.join(subsystems)}."

        hypo = RuntimeCausalHypothesis(
            tenant_id=tenant_id,
            hypothesis_statement=hypothesis_statement,
            status=status,
            confidence=confidence,
            evidence_ids=evidence_ids,
            explanation_notes=notes,
        )
        logger.info(
            f"Formulated RuntimeCausalHypothesis '{hypo.hypothesis_id}' (Status: {status}, Confidence: {confidence})"
        )
        return hypo
