"""Pydantic request/response schemas for Runtime Intelligence (Phase 5.57)."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class RuntimeSignalIngestRequest(BaseModel):
    signal_type: str = Field(..., description="Signal type (HEALTH, PERFORMANCE, SECURITY, etc.)")
    severity: str = Field("INFO", description="Severity level")
    payload: Dict[str, Any] = Field(default_factory=dict)
    source_domain: str = Field("operations", description="Source domain")


class RuntimeSignalResponse(BaseModel):
    signal_id: str
    tenant_id: str
    signal_type: str
    severity: str
    payload: Dict[str, Any]
    created_at: datetime


class RuntimeObservationRequest(BaseModel):
    subsystem: str = Field(..., description="Subsystem name")
    metric_name: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    dimensions: Dict[str, str] = Field(default_factory=dict)


class RuntimeObservationResponse(BaseModel):
    observation_id: str
    tenant_id: str
    subsystem: str
    metric_name: str
    value: float
    observed_at: datetime


class HealthAssessmentRequest(BaseModel):
    subsystem: str = Field(..., description="Subsystem name")
    raw_telemetry: Dict[str, Any] = Field(default_factory=dict)


class HealthAssessmentResponse(BaseModel):
    health_id: str
    tenant_id: str
    subsystem: str
    status: str
    overall_score: float
    evaluated_at: datetime


class AnomalyDetectionRequest(BaseModel):
    subsystem: str = Field(..., description="Subsystem name")
    time_series_data: List[Dict[str, Any]] = Field(default_factory=list)


class AnomalyDetectionResponse(BaseModel):
    detection_id: str
    tenant_id: str
    subsystem: str
    anomalies_found: int
    highest_severity: str
    detected_at: datetime


class DriftAnalysisRequest(BaseModel):
    subsystem: str = Field(..., description="Subsystem name")
    current_data: Dict[str, Any] = Field(default_factory=dict)
    baseline_data: Dict[str, Any] = Field(default_factory=dict)


class DriftAnalysisResponse(BaseModel):
    drift_id: str
    tenant_id: str
    subsystem: str
    drift_detected: bool
    drift_score: float
    analyzed_at: datetime


class BaselineRequest(BaseModel):
    subsystem: str = Field(..., description="Subsystem name")
    metric_name: str = Field(..., description="Metric name")
    sample_values: List[float] = Field(..., description="Sample values")


class BaselineResponse(BaseModel):
    baseline_id: str
    tenant_id: str
    subsystem: str
    metric_name: str
    mean: float
    std_dev: float
    sample_count: int
    established_at: datetime


class DegradationRequest(BaseModel):
    subsystem: str = Field(..., description="Subsystem name")
    historical_scores: List[float] = Field(default_factory=list)


class DegradationResponse(BaseModel):
    analysis_id: str
    tenant_id: str
    subsystem: str
    degradation_trend: str
    estimated_time_to_critical_seconds: float


class CausalAnalysisRequest(BaseModel):
    symptom_id: str = Field(..., description="Symptom ID")
    affected_subsystems: List[str] = Field(default_factory=list)


class CausalAnalysisResponse(BaseModel):
    analysis_id: str
    tenant_id: str
    symptom_id: str
    root_cause: str
    confidence_score: float
    analyzed_at: datetime


class ResilienceAssessmentRequest(BaseModel):
    subsystem: str = Field(..., description="Subsystem name")


class ResilienceAssessmentResponse(BaseModel):
    assessment_id: str
    tenant_id: str
    subsystem: str
    resilience_score: float
    overall_status: str
    evaluated_at: datetime


class RecoveryPlanRequest(BaseModel):
    failed_subsystem: str = Field(..., description="Failed subsystem name")


class RecoveryPlanResponse(BaseModel):
    plan_id: str
    tenant_id: str
    failed_subsystem: str
    steps_count: int
    created_at: datetime


class AdaptiveAssuranceRequest(BaseModel):
    target_subsystem: str = Field(..., description="Target subsystem name")


class AdaptiveAssuranceResponse(BaseModel):
    posture_id: str
    tenant_id: str
    target_subsystem: str
    current_level: str
    recommended_level: str
    evaluated_at: datetime


class RecommendationRequest(BaseModel):
    subsystem: str = Field(..., description="Subsystem name")


class RecommendationResponse(BaseModel):
    recommendation_id: str
    tenant_id: str
    recommendation_type: str
    action_description: str
    priority: str
    auto_execute: bool = False
    created_at: datetime


class GovernanceEvaluationRequest(BaseModel):
    action: str = Field(..., description="Action name")
    risk_level: str = Field("MEDIUM", description="Risk level")


class GovernanceEvaluationResponse(BaseModel):
    evaluation_id: str
    tenant_id: str
    decision: str
    requires_human_approval: bool
    reasoning: str


class DelegationRequestSchema(BaseModel):
    target_domain: str = Field(..., description="Target domain")
    action_type: str = Field(..., description="Action type")
    payload: Dict[str, Any] = Field(default_factory=dict)
    risk_level: str = Field("MEDIUM", description="Risk level")
    is_approved: bool = Field(False, description="Approval status")


class DelegationResponseSchema(BaseModel):
    delegation_id: str
    tenant_id: str
    target_domain: str
    action_type: str
    status: str
    requires_approval: bool
    created_at: datetime


class EvidenceBundleResponse(BaseModel):
    bundle_id: str
    tenant_id: str
    evidence_count: int
    sealed: bool
    integrity_hash: str
    created_at: datetime


class SnapshotResponse(BaseModel):
    snapshot_id: str
    tenant_id: str
    captured_at: datetime
    records_count: int
    integrity_hash: str
