"""Pydantic V2 API Schemas for Continuous Assurance (Phase 5.54)."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class CreateObservationRequest(BaseModel):
    source_domain: str = Field(..., description="Source domain of observation")
    observation_type: str = Field(..., description="Type of runtime observation")
    severity: str = Field(default="INFO", description="Severity level")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Raw observation payload")


class ObservationResponse(BaseModel):
    observation_id: str
    tenant_id: str
    source_domain: str
    observation_type: str
    severity: str
    status: str
    observed_at: datetime


class AssessmentRequest(BaseModel):
    scope: Optional[str] = Field(default="global", description="Assessment scope")


class AssessmentResponse(BaseModel):
    assessment_id: str
    tenant_id: str
    overall_score: float
    state: str
    findings_count: int
    created_at: datetime


class DriftAnalysisRequest(BaseModel):
    drift_type: str = Field(..., description="Target drift dimension")
    expected_state: Dict[str, Any] = Field(default_factory=dict)
    observed_state: Dict[str, Any] = Field(default_factory=dict)


class DriftResponse(BaseModel):
    drift_id: str
    tenant_id: str
    drift_type: str
    severity: str
    difference_summary: str
    confidence: float
    status: str
    detected_at: datetime


class ControlEvaluationRequest(BaseModel):
    control_id: str = Field(..., description="Control identifier")


class ControlEvaluationResponse(BaseModel):
    assessment_id: str
    tenant_id: str
    control_id: str
    status: str
    score: float
    evaluated_at: datetime


class VerificationRequestSchema(BaseModel):
    target_resource_id: str = Field(..., description="Resource ID to verify")
    expected_hash: str = Field(..., description="Expected baseline SHA-256 hash")
    actual_hash: str = Field(..., description="Observed runtime SHA-256 hash")


class VerificationResponse(BaseModel):
    verification_id: str
    tenant_id: str
    target_resource_id: str
    status: str
    verified_at: datetime


class RecommendationRequest(BaseModel):
    target_control: str = Field(..., description="Target control or policy")
    action_description: str = Field(..., description="Proposed recommendation action")
    reason: str = Field(default="Automated adaptive assurance recommendation")


class RecommendationResponse(BaseModel):
    recommendation_id: str
    tenant_id: str
    target_control: str
    action_description: str
    priority: str
    confidence: float
    auto_execute: bool
    created_at: datetime


class GovernanceEvaluationRequest(BaseModel):
    action_type: str = Field(..., description="Action category being evaluated")
    risk_level: str = Field(default="MEDIUM", description="Assessed risk level")


class GovernanceEvaluationResponse(BaseModel):
    outcome: str
    action_type: str
    risk_level: str
    requires_approval: bool
    rationale: str


class DelegationRequestSchema(BaseModel):
    action_name: str = Field(..., description="Target external action name")
    parameters: Dict[str, Any] = Field(default_factory=dict)


class DelegationResponse(BaseModel):
    delegation_id: str
    tenant_id: str
    action_name: str
    status: str
    created_at: datetime
