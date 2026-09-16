"""Pydantic request/response schemas for Capacity Intelligence (Phase 5.56)."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ResourceRegisterRequest(BaseModel):
    resource_id: str = Field(..., description="Resource ID")
    resource_type: str = Field("COMPUTE", description="Resource type")
    total_capacity: float = Field(..., description="Total capacity value")
    unit: str = Field("cores", description="Capacity unit")


class ResourceProfileResponse(BaseModel):
    profile_id: str
    tenant_id: str
    resource_id: str
    resource_type: str
    total_capacity: float
    unit: str
    created_at: datetime


class ResourceRegistrationRequest(BaseModel):
    resource_id: str = Field(..., description="Resource ID")
    name: str = Field(..., description="Resource name")
    resource_type: str = Field(..., description="Resource type")
    total_capacity: float = Field(..., description="Total capacity")
    capacity_unit: str = Field("units", description="Capacity unit")


class ResourceRegistrationResponse(BaseModel):
    resource_id: str
    tenant_id: str
    name: str
    resource_type: str
    total_capacity: float
    capacity_unit: str
    registered_at: datetime


class TelemetryIngestionRequest(BaseModel):
    resource_id: str = Field(..., description="Resource ID")
    metric_name: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    timestamp: Optional[datetime] = None


class TelemetryIngestionResponse(BaseModel):
    telemetry_id: str
    tenant_id: str
    resource_id: str
    metric_name: str
    value: float
    timestamp: datetime


class CapacityAssessmentRequest(BaseModel):
    resource_id: str = Field(..., description="Resource ID")
    scope: str = Field("RESOURCE", description="Assessment scope")


class CapacityAssessmentResponse(BaseModel):
    assessment_id: str
    tenant_id: str
    resource_id: str
    utilization_rate: float
    health_status: str
    assessed_at: datetime


class CapacityForecastRequest(BaseModel):
    resource_id: str = Field(..., description="Resource ID")
    horizon_days: int = Field(30, description="Forecast horizon in days")


class CapacityForecastResponse(BaseModel):
    forecast_id: str
    tenant_id: str
    resource_id: str
    horizon_days: int
    predicted_utilization: float
    exhaustion_predicted: bool
    forecasted_at: datetime


class DemandPredictionRequest(BaseModel):
    workload_type: str = Field(..., description="Workload type")
    time_horizon_hours: int = Field(24, description="Time horizon in hours")


class DemandPredictionResponse(BaseModel):
    prediction_id: str
    tenant_id: str
    workload_type: str
    predicted_growth_rate: float
    confidence_score: float
    predicted_at: datetime


class SaturationAnalysisRequest(BaseModel):
    resource_id: str = Field(..., description="Resource ID")


class SaturationAnalysisResponse(BaseModel):
    analysis_id: str
    tenant_id: str
    resource_id: str
    saturation_level: float
    headroom_percent: float
    analyzed_at: datetime


class BottleneckDetectionRequest(BaseModel):
    system_scope: str = Field("GLOBAL", description="System scope")


class BottleneckDetectionResponse(BaseModel):
    detection_id: str
    tenant_id: str
    bottlenecks_found: int
    critical_count: int
    detected_at: datetime


class OptimizationRequest(BaseModel):
    resource_id: str = Field(..., description="Resource ID")
    objective: str = Field("COST_PERFORMANCE", description="Optimization objective")


class OptimizationResponse(BaseModel):
    plan_id: str
    tenant_id: str
    resource_id: str
    objective: str
    auto_execute: bool = False
    recommendations_count: int
    created_at: datetime


class CostPerformanceRequest(BaseModel):
    resource_id: str = Field(..., description="Resource ID")


class CostPerformanceResponse(BaseModel):
    assessment_id: str
    tenant_id: str
    resource_id: str
    efficiency_score: float
    cost_per_unit: float
    evaluated_at: datetime


class GovernanceRequest(BaseModel):
    action: str = Field(..., description="Action name")
    risk_level: str = Field("MEDIUM", description="Risk level")


class GovernanceResponse(BaseModel):
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


class CapacityRecommendationResponse(BaseModel):
    recommendation_id: str
    tenant_id: str
    target_resource_id: str
    recommendation_type: str
    action_description: str
    priority: str
    auto_execute: bool = False
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
