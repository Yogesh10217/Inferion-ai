"""Canonical Domain Normalization Adapters for Phase 5.58 Platform Integration."""

import logging
import uuid
from typing import Any, Dict, Optional

from app.platform_integration.models import (
    CrossPhaseAssessment,
    CrossPhaseFinding,
    CrossPhaseSignal,
    IntegrationPlatform,
    TraceContext,
)

logger = logging.getLogger(__name__)


class DomainNormalizer:
    """Normalizes heterogeneous intelligence payloads into standard CrossPhase data structures."""

    @staticmethod
    def normalize_signal(
        tenant_id: str,
        platform: str,
        raw_signal: Dict[str, Any],
        trace_context: Optional[TraceContext] = None,
    ) -> CrossPhaseSignal:
        p_enum = IntegrationPlatform[platform.upper()] if platform.upper() in IntegrationPlatform.__members__ else IntegrationPlatform.RUNTIME
        sig_id = raw_signal.get("signal_id", f"sig-{p_enum.value.lower()}-{uuid.uuid4().hex[:8]}")
        sig_type = raw_signal.get("signal_type", raw_signal.get("type", "TELEMETRY"))
        severity = raw_signal.get("severity", "INFO")
        confidence = float(raw_signal.get("confidence", 1.0))
        ev_refs = raw_signal.get("evidence_references", [])

        ctx = trace_context or TraceContext(
            tenant_id=tenant_id,
            source_platform=p_enum.value,
        )

        return CrossPhaseSignal(
            signal_id=sig_id,
            tenant_id=tenant_id,
            source_platform=p_enum,
            signal_type=sig_type,
            severity=severity,
            payload=raw_signal.get("payload", raw_signal),
            trace_context=ctx,
            confidence=confidence,
            evidence_references=ev_refs,
        )

    @staticmethod
    def normalize_finding(
        tenant_id: str,
        platform: str,
        raw_finding: Dict[str, Any],
        trace_context: Optional[TraceContext] = None,
    ) -> CrossPhaseFinding:
        p_enum = IntegrationPlatform[platform.upper()] if platform.upper() in IntegrationPlatform.__members__ else IntegrationPlatform.RUNTIME
        f_id = raw_finding.get("finding_id", f"find-{p_enum.value.lower()}-{uuid.uuid4().hex[:8]}")
        title = raw_finding.get("title", f"{p_enum.value} Finding")
        desc = raw_finding.get("description", raw_finding.get("summary", ""))
        severity = raw_finding.get("severity", "LOW")
        impact = float(raw_finding.get("impact", raw_finding.get("impact_score", 0.1)))
        ev_refs = raw_finding.get("evidence_references", [])

        ctx = trace_context or TraceContext(
            tenant_id=tenant_id,
            source_platform=p_enum.value,
        )

        return CrossPhaseFinding(
            finding_id=f_id,
            tenant_id=tenant_id,
            source_platform=p_enum,
            title=title,
            description=desc,
            severity=severity,
            impact_score=impact,
            trace_context=ctx,
            attributes=raw_finding.get("attributes", {}),
            evidence_references=ev_refs,
        )

    @staticmethod
    def normalize_assessment(
        tenant_id: str,
        platform: str,
        raw_assessment: Dict[str, Any],
        trace_context: Optional[TraceContext] = None,
    ) -> CrossPhaseAssessment:
        p_enum = IntegrationPlatform[platform.upper()] if platform.upper() in IntegrationPlatform.__members__ else IntegrationPlatform.RUNTIME
        a_id = raw_assessment.get("assessment_id", f"ass-{p_enum.value.lower()}-{uuid.uuid4().hex[:8]}")
        a_type = raw_assessment.get("assessment_type", f"{p_enum.value}_POSTURE")
        score = float(raw_assessment.get("score", raw_assessment.get("assurance_score", 0.9)))
        posture = raw_assessment.get("posture", raw_assessment.get("status", "ASSURED"))
        confidence = float(raw_assessment.get("confidence", 0.95))
        uncertainty = float(raw_assessment.get("uncertainty", 0.05))
        ev_refs = raw_assessment.get("evidence_references", [])

        ctx = trace_context or TraceContext(
            tenant_id=tenant_id,
            source_platform=p_enum.value,
        )

        return CrossPhaseAssessment(
            assessment_id=a_id,
            tenant_id=tenant_id,
            source_platform=p_enum,
            assessment_type=a_type,
            score=score,
            posture=posture,
            confidence=confidence,
            uncertainty=uncertainty,
            trace_context=ctx,
            details=raw_assessment.get("details", raw_assessment),
            evidence_references=ev_refs,
        )
