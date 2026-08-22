"""SQLAlchemy Persistence Models for Developer Platform Subsystems."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON
from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class DeveloperProjectModel(Base):
    __tablename__ = "dev_projects"

    project_id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(64), nullable=False, default="ACTIVE", index=True)
    tenant_id = Column(String(64), nullable=False, index=True)

    created_at = Column(DateTime, nullable=False, default=_now)
    updated_at = Column(DateTime, nullable=False, default=_now, onupdate=_now)


class RepositoryModel(Base):
    __tablename__ = "dev_repositories"

    repository_id = Column(String(64), primary_key=True, index=True)
    project_id = Column(String(64), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    provider = Column(String(64), nullable=False, default="github")
    default_branch = Column(String(64), nullable=False, default="main")
    tenant_id = Column(String(64), nullable=False, index=True)

    created_at = Column(DateTime, nullable=False, default=_now)


class APIProductModel(Base):
    __tablename__ = "dev_api_products"

    service_id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    version = Column(String(64), nullable=False, default="1.0.0")
    status = Column(String(64), nullable=False, default="PUBLISHED", index=True)
    tenant_id = Column(String(64), nullable=False, index=True)

    created_at = Column(DateTime, nullable=False, default=_now)


class PipelineModel(Base):
    __tablename__ = "dev_pipelines"

    pipeline_id = Column(String(64), primary_key=True, index=True)
    project_id = Column(String(64), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)

    created_at = Column(DateTime, nullable=False, default=_now)


class SoftwareReleaseModel(Base):
    __tablename__ = "dev_software_releases"

    release_id = Column(String(64), primary_key=True, index=True)
    project_id = Column(String(64), nullable=False, index=True)
    version = Column(String(64), nullable=False, default="1.0.0")
    status = Column(String(64), nullable=False, default="DEPLOYED", index=True)
    tenant_id = Column(String(64), nullable=False, index=True)

    created_at = Column(DateTime, nullable=False, default=_now)
