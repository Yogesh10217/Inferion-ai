"""SQLAlchemy Persistence Models for Identity Platform Domain Entities."""

from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, Column, DateTime, String

from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class IdentityModel(Base):
    __tablename__ = "identities"

    identity_id = Column(String(64), primary_key=True, index=True)
    username = Column(String(255), nullable=False)
    identity_type = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False)
    tenant_id = Column(String(64), index=True, nullable=False, default="global")
    organization_id = Column(String(64), nullable=True)
    workspace_id = Column(String(64), nullable=True)
    project_id = Column(String(64), nullable=True)
    roles = Column(JSON, nullable=False, default=list)
    profile = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)


class AuthenticationSessionModel(Base):
    __tablename__ = "authentication_sessions"

    session_id = Column(String(64), primary_key=True, index=True)
    identity_id = Column(String(64), index=True, nullable=False)
    tenant_id = Column(String(64), index=True, nullable=False, default="global")
    state = Column(String(32), nullable=False)
    access_token = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=False)
    ip_address = Column(String(64), nullable=False)
    is_restricted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)


class CredentialModel(Base):
    __tablename__ = "credentials"

    credential_id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    identity_id = Column(String(64), index=True, nullable=False)
    tenant_id = Column(String(64), index=True, nullable=False, default="global")
    credential_type = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False)
    scopes = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
