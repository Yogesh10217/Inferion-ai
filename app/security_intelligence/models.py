"""SQLAlchemy Database ORM Models for Security Intelligence (Phase 5.32)."""

from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, Float, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class SecurityAssetModel(Base):
    __tablename__ = "security_assets"

    asset_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    asset_type = Column(String(32), nullable=False)
    criticality = Column(String(32), nullable=False)
    exposure = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False)
    architecture_node_id = Column(String(64), nullable=True)
    metadata_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class SecuritySignalModel(Base):
    __tablename__ = "security_signals"

    signal_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    asset_id = Column(String(64), nullable=False, index=True)
    signal_type = Column(String(64), nullable=False)
    severity = Column(String(32), nullable=False)
    source = Column(String(64), nullable=False)
    payload_json = Column(JSON, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class SecurityThreatModel(Base):
    __tablename__ = "security_threats"

    threat_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    asset_id = Column(String(64), nullable=False, index=True)
    threat_type = Column(String(64), nullable=False)
    severity = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False)
    confidence = Column(String(32), nullable=False)
    evidence_references_json = Column(JSON, nullable=False)
    detected_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class AIThreatModel(Base):
    __tablename__ = "security_ai_threats"

    ai_threat_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    model_or_agent_id = Column(String(64), nullable=False, index=True)
    threat_type = Column(String(64), nullable=False)
    severity = Column(String(32), nullable=False)
    detections_json = Column(JSON, nullable=False)
    detected_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class SecurityVulnerabilityModel(Base):
    __tablename__ = "security_vulnerabilities"

    vulnerability_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    asset_id = Column(String(64), nullable=False, index=True)
    title = Column(String(256), nullable=False)
    severity = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False)
    evidence_json = Column(JSON, nullable=True)
    discovered_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class AttackPathModel(Base):
    __tablename__ = "security_attack_paths"

    path_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    title = Column(String(256), nullable=False)
    nodes_json = Column(JSON, nullable=False)
    edges_json = Column(JSON, nullable=False)
    risk_level = Column(String(32), nullable=False)
    exposure_score = Column(Float, nullable=False)
    dependency_concentration = Column(Float, nullable=False)
    analyzed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class SecurityIncidentModel(Base):
    __tablename__ = "security_incidents"

    incident_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    asset_id = Column(String(64), nullable=False, index=True)
    title = Column(String(256), nullable=False)
    severity = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False)
    timeline_json = Column(JSON, nullable=False)
    fingerprint = Column(String(128), nullable=True)
    finalized_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class SecurityInvestigationModel(Base):
    __tablename__ = "security_investigations"

    investigation_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    incident_id = Column(String(64), nullable=False, index=True)
    title = Column(String(256), nullable=False)
    status = Column(String(32), nullable=False)
    findings_json = Column(JSON, nullable=False)
    snapshot_json = Column(JSON, nullable=True)
    fingerprint = Column(String(128), nullable=True)
    finalized_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class SecurityRemediationModel(Base):
    __tablename__ = "security_remediations"

    plan_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    incident_id = Column(String(64), nullable=False, index=True)
    idempotency_key = Column(String(128), nullable=False)
    priority = Column(String(32), nullable=False)
    actions_json = Column(JSON, nullable=False)
    status = Column(String(32), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class SecurityEvidenceModel(Base):
    __tablename__ = "security_evidences"

    bundle_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    title = Column(String(256), nullable=False)
    evidences_json = Column(JSON, nullable=False)
    fingerprint = Column(String(128), nullable=True)
    finalized_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class SecurityPostureModel(Base):
    __tablename__ = "security_postures"

    posture_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    overall_score = Column(Float, nullable=False)
    band = Column(String(32), nullable=False)
    dimensions_json = Column(JSON, nullable=False)
    calculated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class SecurityTrustModel(Base):
    __tablename__ = "security_trust_scores"

    asset_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    score = Column(Float, nullable=False)
    calculated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")
