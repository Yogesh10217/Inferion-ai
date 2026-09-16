"""Pydantic v2 API Schemas for Platform Integration (Phase 5.58)."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ContextBuildRequest(BaseModel):
    trace_id: Optional[str] = None
    correlation_id: Optional[str] = None


class ContextResponse(BaseModel):
    context_id: str
    tenant_id: str
    active_platforms: List[str]
    signals_count: int
    findings_count: int
    fingerprint: str


class CorrelateRequest(BaseModel):
    threshold: float = 0.5


class CorrelateResponse(BaseModel):
    correlations_count: int
    correlations: List[Dict[str, Any]]


class AssuranceResponse(BaseModel):
    overall_score: float
    confidence: float
    uncertainty: float
    trust_band: str
    posture: str
    degraded_platforms: List[str]


class InvestigationRequest(BaseModel):
    root_platform: str
    incident_description: str


class InvestigationResponse(BaseModel):
    investigation_id: str
    root_platform: str
    traversed_platforms: List[str]
    conclusion: str
    evidence_count: int


class RecommendationResponse(BaseModel):
    recommendations: List[Dict[str, Any]]


class DelegationCreateRequest(BaseModel):
    recommendation_id: str
    approval_id: Optional[str] = None
    approval_token: Optional[str] = None


class DelegationResponse(BaseModel):
    delegation_id: str
    action: str
    target: str
    status: str


class VerificationRequest(BaseModel):
    delegation_id: str
    pre_score: float
    post_score: float
    required_delta: float = 0.05


class VerificationResponse(BaseModel):
    verification_id: str
    status: str
    verified: bool
    improvement_delta: float


class SnapshotCaptureResponse(BaseModel):
    snapshot_id: str
    fingerprint: str
    score: float
