"""
Pydantic API Request/Response Schemas for Platform Hardening.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.platform_hardening.models import (
    IntegrationHealthStatus,
    PlatformAuditSeverity,
    PlatformAuditStatus,
    PlatformCertificationStatus,
    ReleaseReadinessDecision,
)


class PlatformAuditRequest(BaseModel):
    tenant_id: str = Field(..., description="Tenant identifier")
    include_ast_scan: bool = Field(True, description="Whether to include AST code scanning")
    include_cross_phase_validation: bool = Field(True, description="Whether to perform cross-phase validations")
    include_api_contract_validation: bool = Field(True, description="Whether to validate API & SDK contracts")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FindingSchema(BaseModel):
    finding_id: str
    tenant_id: str
    rule_id: str
    title: str
    description: str
    severity: PlatformAuditSeverity
    subsystem: str
    affected_component: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    root_cause_hypothesis: Optional[str] = None
    remediation_suggestion: Optional[str] = None
    evidence_reference: Optional[str] = None
    created_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RemediationSchema(BaseModel):
    remediation_id: str
    tenant_id: str
    finding_id: str
    severity: PlatformAuditSeverity
    subsystem: str
    affected_component: str
    root_cause_hypothesis: str
    recommendation: str
    risk: str
    priority: str
    requires_approval: bool = True
    auto_execute: bool = False
    created_at: datetime


class CertificationSchema(BaseModel):
    certification_id: str
    tenant_id: str
    status: PlatformCertificationStatus
    release_decision: ReleaseReadinessDecision
    overall_score: float
    sha256_hash: str
    audited_phases_count: int
    certified_at: datetime
    details: Dict[str, Any] = Field(default_factory=dict)


class PlatformAuditResponse(BaseModel):
    audit_id: str
    tenant_id: str
    status: PlatformAuditStatus
    findings_count: int
    critical_findings_count: int
    readiness_score: float
    release_decision: ReleaseReadinessDecision
    certification_status: PlatformCertificationStatus
    findings: List[FindingSchema] = Field(default_factory=list)
    remediations: List[RemediationSchema] = Field(default_factory=list)
    certification: Optional[CertificationSchema] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


class PlatformHealthResponse(BaseModel):
    tenant_id: str
    integration_health: IntegrationHealthStatus
    certification_status: PlatformCertificationStatus
    release_readiness: ReleaseReadinessDecision
    readiness_score: float
    total_findings: int
    critical_findings: int
    timestamp: datetime


class SubsystemHealthSchema(BaseModel):
    subsystem_name: str
    phase: str
    status: IntegrationHealthStatus
    provider_name: Optional[str] = None
    sdk_available: bool
    cli_available: bool
    health_score: float


class IntegrationHealthResponse(BaseModel):
    overall_health: IntegrationHealthStatus
    overall_health_score: float
    subsystems: List[SubsystemHealthSchema] = Field(default_factory=list)


class CertificationRequest(BaseModel):
    tenant_id: str = Field(..., description="Tenant identifier")
    force_audit: bool = Field(False, description="Whether to trigger a fresh audit before certification")


class CertificationResponse(BaseModel):
    certification_id: str
    tenant_id: str
    status: PlatformCertificationStatus
    release_decision: ReleaseReadinessDecision
    overall_score: float
    sha256_hash: str
    audited_phases_count: int
    certified_at: datetime
    details: Dict[str, Any] = Field(default_factory=dict)


class ReadinessResponse(BaseModel):
    tenant_id: str
    readiness_score: float
    release_decision: ReleaseReadinessDecision
    architecture_score: float
    integration_score: float
    reliability_score: float
    security_score: float
    governance_score: float
    traceability_score: float
    evidence_score: float
    testing_score: float
    maintainability_score: float
    critical_blockers_count: int


class RemediationResponse(BaseModel):
    tenant_id: str
    total_remediations: int
    remediations: List[RemediationSchema] = Field(default_factory=list)


class GenericValidationRequest(BaseModel):
    tenant_id: str = Field(..., description="Tenant identifier")
    params: Dict[str, Any] = Field(default_factory=dict)


class GenericValidationResponse(BaseModel):
    tenant_id: str
    is_valid: bool
    findings_count: int
    details: Dict[str, Any] = Field(default_factory=dict)
