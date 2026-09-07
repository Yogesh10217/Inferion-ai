"""
Pydantic Schemas for Phase 5.52 Enterprise AI Decision Intelligence Platform.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DecisionCreateRequest(BaseModel):
    title: str = Field(..., description="Title of the decision request")
    description: Optional[str] = Field(None, description="Detailed description")
    decision_type: str = Field("OPERATIONAL", description="Type of decision (OPERATIONAL, SECURITY, ARCHITECTURAL, POLICY)")
    scope: str = Field("ENTERPRISE", description="Scope of the decision")
    risk_level: str = Field("MEDIUM", description="Assessed risk level (LOW, MEDIUM, HIGH, CRITICAL)")
    input_signals: List[Dict[str, Any]] = Field(default_factory=list, description="Input domain signals")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context metadata")


class DecisionOptionCreateRequest(BaseModel):
    title: str = Field(..., description="Option title")
    description: Optional[str] = Field(None, description="Option description")
    action_type: str = Field("DELEGATE", description="Action type for the option")
    target_system: str = Field("OPERATIONS", description="Target system")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    estimated_cost: float = Field(0.0, description="Estimated monetary/resource cost")
    reversibility: str = Field("REVERSIBLE", description="Reversibility rating (REVERSIBLE, PARTIALLY_REVERSIBLE, IRREVERSIBLE)")


class DecisionStateTransitionRequest(BaseModel):
    target_state: str = Field(..., description="Target lifecycle state")
    reason: Optional[str] = Field(None, description="Reason for transition")


class DecisionApprovalRequest(BaseModel):
    approver: str = Field(..., description="Approver identity")
    approved: bool = Field(..., description="Whether approved or rejected")
    comments: Optional[str] = Field(None, description="Approval comments")


class DecisionSimulationRequest(BaseModel):
    options: List[Dict[str, Any]] = Field(default_factory=list, description="Options to simulate")
    scenarios: List[str] = Field(default_factory=lambda: ["HIGH_LOAD", "FAILOVER", "SECURITY_SPIKE"])
    simulation_depth: str = Field("DETAILED", description="Depth of simulation")


class DecisionResponse(BaseModel):
    id: str
    tenant_id: str
    title: str
    description: Optional[str] = None
    state: str
    decision_type: str
    scope: str
    risk_level: str
    confidence_score: float = 0.0
    uncertainty_score: float = 0.0
    created_at: str
    updated_at: str
    fingerprint: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DecisionOptionResponse(BaseModel):
    id: str
    decision_id: str
    tenant_id: str
    title: str
    description: Optional[str] = None
    action_type: str
    target_system: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    score: float = 0.0
    estimated_cost: float = 0.0
    reversibility: str = "REVERSIBLE"


class DecisionRecommendationResponse(BaseModel):
    id: str
    decision_id: str
    tenant_id: str
    recommended_option_id: str
    rationale: str
    confidence: float
    uncertainty: float
    auto_execute: bool = False
    requires_approval: bool = True
    created_at: str


class DecisionSimulationResultResponse(BaseModel):
    simulation_id: str
    decision_id: str
    tenant_id: str
    compared_options: List[Dict[str, Any]]
    best_option_id: Optional[str]
    tradeoffs: List[Dict[str, Any]]
    simulated_impact: Dict[str, Any]
    simulated_risk: Dict[str, Any]


class DecisionReproducibilityRecordResponse(BaseModel):
    id: str
    decision_id: str
    tenant_id: str
    context_fingerprint: str
    evidence_hashes: List[str]
    model_version: str
    scoring_config_version: str
    policy_evaluation_id: str
    risk_assessment_id: str
    timestamp: str
