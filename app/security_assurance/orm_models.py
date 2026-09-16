"""ORM Models for Security Assurance Entities."""

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class SecurityAssetORM(BaseModel):
    asset_id: str
    tenant_id: str
    name: str
    asset_type: str
    criticality: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityIncidentORM(BaseModel):
    incident_id: str
    tenant_id: str
    title: str
    severity: str
    state: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
