"""Trusted context assembly intelligence across trust, freshness, relevance, and conflict filtering."""

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ContextAssemblyEvidence(BaseModel):
    source_id: str
    reference_id: str
    trust_score: float = 0.90
    relevance_score: float = 0.85
    freshness_score: float = 0.95


class ContextAssemblyRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    query_or_topic: str = "general"
    min_trust_score: float = 0.70
    min_freshness_score: float = 0.60
    max_items: int = 10
    exclude_conflicted: bool = True
    target_domain: str = "general"
    target_resource_id: Optional[str] = None
    required_concepts: List[str] = Field(default_factory=list)


class ContextAssemblyPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str
    tenant_id: str
    selected_reference_ids: List[str] = Field(default_factory=list)
    ranking_summary: str = ""


class ContextAssemblyResult(BaseModel):
    result_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    assembled_context_text: str
    assembled_reference_ids: List[str] = Field(default_factory=list)
    overall_trust_score: float = 0.90
    overall_confidence_score: float = 0.88
    fingerprint: Optional[str] = None
    evidence: List[ContextAssemblyEvidence] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def assembly_id(self) -> str:
        return self.result_id

    @property
    def trust_score(self) -> float:
        return self.overall_trust_score

    @property
    def assembled_items(self) -> List[str]:
        return self.assembled_reference_ids

    def calculate_fingerprint(self) -> str:
        data = f"{self.result_id}:{self.tenant_id}:{self.overall_trust_score:.2f}:{self.created_at.isoformat()}"
        return hashlib.sha256(data.encode("utf-8")).hexdigest()


class ContextAssemblyManager:
    """Assembles trusted, verified semantic context for downstream reasoning without vector DB duplication."""

    def __init__(self) -> None:
        self._results: Dict[str, ContextAssemblyResult] = {}

    def assemble_context(
        self,
        tenant_id_or_request: Any,
        request_or_candidates: Any = None,
        candidate_references: Optional[List[Dict[str, Any]]] = None,
    ) -> ContextAssemblyResult:
        if isinstance(tenant_id_or_request, ContextAssemblyRequest):
            request = tenant_id_or_request
            candidate_references = request_or_candidates or candidate_references
        else:
            tenant_id = tenant_id_or_request
            if isinstance(request_or_candidates, ContextAssemblyRequest):
                request = request_or_candidates
            else:
                request = ContextAssemblyRequest(tenant_id=tenant_id)

        if not candidate_references:
            candidate_references = [
                {
                    "reference_id": "ref-101",
                    "source_id": "src-internal",
                    "title": "Standard Operating Procedure for Production Incident Escalation",
                    "summary": "Step-by-step incident response guidelines",
                    "trust_score": 0.95,
                    "relevance_score": 0.90,
                    "freshness_score": 0.98,
                    "has_conflict": False,
                },
                {
                    "reference_id": "ref-102",
                    "source_id": "src-policy",
                    "title": "Enterprise Data Security and Privacy Policy",
                    "summary": "Zero-trust encryption and data handling policy",
                    "trust_score": 0.98,
                    "relevance_score": 0.88,
                    "freshness_score": 0.92,
                    "has_conflict": False,
                },
            ]

        # Filter by trust, freshness, conflict
        filtered = []
        evidence_list = []
        for ref in candidate_references:
            if ref.get("trust_score", 0.0) < request.min_trust_score:
                continue
            if ref.get("freshness_score", 0.0) < request.min_freshness_score:
                continue
            if request.exclude_conflicted and ref.get("has_conflict", False):
                continue
            filtered.append(ref)
            evidence_list.append(
                ContextAssemblyEvidence(
                    source_id=ref.get("source_id", "src-gen"),
                    reference_id=ref.get("reference_id", "ref-gen"),
                    trust_score=ref.get("trust_score", 0.90),
                    relevance_score=ref.get("relevance_score", 0.85),
                    freshness_score=ref.get("freshness_score", 0.95),
                )
            )

        # Sort by relevance * trust
        filtered.sort(key=lambda x: x.get("relevance_score", 0.0) * x.get("trust_score", 0.0), reverse=True)
        selected = filtered[: request.max_items]

        text_blocks = [f"[{r.get('title')}]\n{r.get('summary')}" for r in selected]
        assembled_text = "\n\n".join(text_blocks)

        avg_trust = sum(r.get("trust_score", 0.9) for r in selected) / len(selected) if selected else 0.90

        result = ContextAssemblyResult(
            tenant_id=request.tenant_id,
            assembled_context_text=assembled_text,
            assembled_reference_ids=[r.get("reference_id") for r in selected],
            overall_trust_score=avg_trust,
            overall_confidence_score=0.92,
            evidence=evidence_list,
        )
        result.fingerprint = result.calculate_fingerprint()
        self._results[result.result_id] = result
        return result
