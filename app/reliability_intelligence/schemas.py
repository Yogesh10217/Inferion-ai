"""Pydantic V2 API Schemas for Reliability Intelligence (Phase 5.55)."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class ServiceHealthRequest(BaseModel):
    service_id: str = Field(..., description="Target service identifier")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Raw metrics data")


class ServiceHealthResponse(BaseModel):
    assessment_id: str
    tenant_id: str
    service_id: str
    status: str
    overall_score: float
    evaluated_at: datetime


class ReliabilityAssessmentRequest(BaseModel):
    scope: Optional[str] = Field(default="global", description="Scope of assessment")


class ReliabilityAssessmentResponse(BaseModel):
    assessment_id: str
    tenant_id: str
    overall_score: float
    state: str
    findings_count: int
    created_at: datetime


class SLORequest(BaseModel):
    service_id: str = Field(..., description="Service ID")
    indicator_type: str = Field(default="AVAILABILITY", description="SLI indicator type")
    target_percentage: float = Field(default=99.9, description="Target SLO percentage")


class SLOResponse(BaseModel):
    slo_id: str
    tenant_id: str
    service_id: str
    indicator_type: str
    target_percentage: float
    current_percentage: float
    is_breached: bool


class ErrorBudgetResponse(BaseModel):
    slo_id: str
    tenant_id: str
    total_budget_minutes: float
    remaining_budget_minutes: float
    status: str
    burn_rate: float


class PredictionRequest(BaseModel):
    service_id: str = Field(..., description="Service ID to analyze")
    horizon_minutes: int = Field(default=60, description="Prediction time horizon")


class PredictionResponse(BaseModel):
    prediction_id: str
    tenant_id: str
    service_id: str
    predicted_failure_type: str
    probability: float
    confidence: float
    explanation: str
    created_at: datetime


class PropagationRequest(BaseModel):
    origin_service: str = Field(..., description="Origin service ID")


class PropagationResponse(BaseModel):
    path_id: str
    tenant_id: str
    origin_service: str
    affected_nodes: List[str]
    propagation_probability: float
    blast_radius_score: float


class ResilienceAssessmentRequest(BaseModel):
    service_id: str = Field(..., description="Service ID")


class ResilienceAssessmentResponse(BaseModel):
    assessment_id: str
    tenant_id: str
    service_id: str
    score: float
    redundancy_level: str
    circuit_breaker_active: bool


class DegradationPlanRequest(BaseModel):
    service_id: str = Field(..., description="Service ID")
    strategy: str = Field(default="GRACEFUL", description="Degradation strategy")


class DegradationPlanResponse(BaseModel):
    plan_id: str
    tenant_id: str
    service_id: str
    strategy: str
    requires_approval: bool


class RecoveryPlanRequest(BaseModel):
    service_id: str = Field(..., description="Service ID")
    strategy: str = Field(default="FAILOVER", description="Recovery strategy")


class RecoveryPlanResponse(BaseModel):
    plan_id: str
    tenant_id: str
    service_id: str
    strategy: str
    estimated_rto_minutes: float


class ChaosProposalRequest(BaseModel):
    experiment_name: str = Field(..., description="Name of proposed chaos experiment")
    target_service: str = Field(..., description="Target service")
    hypothesis: str = Field(..., description="Test hypothesis")


class ChaosProposalResponse(BaseModel):
    proposal_id: str
    tenant_id: str
    experiment_name: str
    target_service: str
    risk_level: str
    requires_approval: bool
    auto_execute: bool


class GovernanceRequest(BaseModel):
    action_type: str = Field(..., description="Reliability action category")
    risk_level: str = Field(default="MEDIUM", description="Assessed risk level")


class GovernanceResponse(BaseModel):
    outcome: str
    action_type: str
    risk_level: str
    requires_approval: bool
    rationale: str
