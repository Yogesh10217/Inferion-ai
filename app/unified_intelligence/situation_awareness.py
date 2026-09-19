"""Enterprise Situation Awareness Engine (Status vs Severity Separation Invariant)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.unified_intelligence.domains import IntelligenceDomain


class SituationStatus(str, Enum):
    DETECTED = "DETECTED"
    ANALYZING = "ANALYZING"
    WATCH = "WATCH"
    ELEVATED = "ELEVATED"
    HIGH_RISK = "HIGH_RISK"
    CRITICAL = "CRITICAL"
    STABILIZING = "STABILIZING"
    RESOLVED = "RESOLVED"


class SituationSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EnterpriseSituation(BaseModel):
    situation_id: str = Field(default_factory=lambda: f"sit-{uuid.uuid4().hex[:8]}")
    correlation_id: str = Field(default_factory=lambda: f"corr-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    title: str
    description: str = ""
    status: SituationStatus = SituationStatus.DETECTED
    severity: SituationSeverity = SituationSeverity.HIGH
    impacted_domains: List[IntelligenceDomain] = Field(default_factory=list)
    affected_entities: List[str] = Field(default_factory=list)
    evidence_references: List[str] = Field(default_factory=list)
    causal_hypotheses: List[Any] = Field(default_factory=list)
    confidence_score: float = 0.88
    summary: str = ""
    idempotency_key: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def participating_domains(self) -> List[IntelligenceDomain]:
        return self.impacted_domains

    def to_dict(self) -> Dict[str, Any]:
        return {
            "situation_id": self.situation_id,
            "correlation_id": self.correlation_id,
            "tenant_id": self.tenant_id,
            "title": self.title,
            "description": self.description or self.summary,
            "status": self.status.value if hasattr(self.status, "value") else str(self.status),
            "severity": self.severity.value if hasattr(self.severity, "value") else str(self.severity),
            "impacted_domains": [d.value if hasattr(d, "value") else str(d) for d in self.impacted_domains],
            "participating_domains": [d.value if hasattr(d, "value") else str(d) for d in self.impacted_domains],
            "affected_entities": self.affected_entities,
            "evidence_references": self.evidence_references,
            "confidence_score": round(self.confidence_score, 4),
            "summary": self.summary,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class SituationAwarenessEngine:
    """Manages enterprise-wide situation awareness with distinct lifecycle status and severity."""

    def __init__(self) -> None:
        self._situations: Dict[str, EnterpriseSituation] = {}
        self._idempotency_map: Dict[str, str] = {}

    def evaluate_situations(
        self, context: Any, correlations: List[Any], hypotheses: List[Any]
    ) -> List[EnterpriseSituation]:
        if not context.signals:
            return []

        tenant_id = context.tenant_id
        corr_id = correlations[0].correlation_id if correlations else f"corr-{uuid.uuid4().hex[:8]}"

        severities = [getattr(s, "severity", "MEDIUM") for s in context.signals]
        is_critical = any(str(sev).upper() == "CRITICAL" for sev in severities)
        is_high = any(str(sev).upper() == "HIGH" for sev in severities)

        sev = (
            SituationSeverity.CRITICAL
            if is_critical
            else (SituationSeverity.HIGH if is_high else SituationSeverity.MEDIUM)
        )
        stat = SituationStatus.ANALYZING if is_critical or is_high else SituationStatus.WATCH

        entities = list(
            {
                getattr(s, "source_reference", None) or getattr(s, "entity_reference", "entity-1")
                for s in context.signals
            }
        )
        evidence = list({ev for s in context.signals for ev in getattr(s, "evidence_ids", [])})

        title = f"Multi-Domain Event in {[d.value if hasattr(d, 'value') else str(d) for d in context.domains]}"
        sit_id = f"sit-{uuid.uuid4().hex[:8]}"

        sit = EnterpriseSituation(
            situation_id=sit_id,
            correlation_id=corr_id,
            tenant_id=tenant_id,
            title=title,
            description=f"Enterprise situation detected across {len(context.domains)} domains.",
            status=stat,
            severity=sev,
            impacted_domains=context.domains,
            affected_entities=entities,
            evidence_references=evidence,
            causal_hypotheses=hypotheses,
            confidence_score=context.confidence_score,
            summary=context.unified_summary,
        )

        self._situations[sit.situation_id] = sit
        return [sit]

    def evaluate_situation(
        self,
        tenant_id: str,
        title: str,
        impacted_domains: List[IntelligenceDomain],
        severity: SituationSeverity = SituationSeverity.HIGH,
        summary: str = "",
        idempotency_key: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> EnterpriseSituation:
        if idempotency_key and idempotency_key in self._idempotency_map:
            sit_id = self._idempotency_map[idempotency_key]
            return self._situations[sit_id]

        status = (
            SituationStatus.CRITICAL
            if severity == SituationSeverity.CRITICAL
            else (SituationStatus.ELEVATED if severity == SituationSeverity.HIGH else SituationStatus.WATCH)
        )

        sit = EnterpriseSituation(
            correlation_id=correlation_id or f"corr-{uuid.uuid4().hex[:8]}",
            tenant_id=tenant_id,
            title=title,
            status=status,
            severity=severity,
            impacted_domains=impacted_domains,
            summary=summary or f"Enterprise situation evaluated across {len(impacted_domains)} domains.",
            idempotency_key=idempotency_key,
        )

        self._situations[sit.situation_id] = sit
        if idempotency_key:
            self._idempotency_map[idempotency_key] = sit.situation_id

        return sit

    def update_status(self, tenant_id: str, situation_id: str, new_status: SituationStatus) -> EnterpriseSituation:
        sit = self._situations.get(situation_id)
        if not sit:
            raise KeyError(f"Situation '{situation_id}' not found.")
        sit.status = new_status
        sit.updated_at = datetime.now(timezone.utc)
        return sit

    def list_situations(self, tenant_id: str) -> List[EnterpriseSituation]:
        return [s for s in self._situations.values() if s.tenant_id == tenant_id]
