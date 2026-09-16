"""SQLAlchemy ORM models for Intelligence Platform."""

from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, Float, String, Text

from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class IntelligenceSignalModel(Base):
    __tablename__ = "intelligence_signals"

    signal_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    source = Column(String(64), nullable=False)
    signal_type = Column(String(64), nullable=False)
    classification = Column(String(64), nullable=False)
    confidence = Column(String(32), nullable=False)
    message = Column(Text, nullable=False)
    metrics = Column(JSON, default=dict)
    payload = Column(JSON, default=dict)
    resource_id = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now)


class InsightModel(Base):
    __tablename__ = "intelligence_insights"

    insight_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    insight_type = Column(String(64), nullable=False)
    severity = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False)
    observation = Column(Text, nullable=False)
    recommended_next_step = Column(Text, nullable=False)
    confidence = Column(Float, default=0.90)
    created_at = Column(DateTime(timezone=True), default=_now)


class ForecastModel(Base):
    __tablename__ = "intelligence_forecasts"

    forecast_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    target_resource_id = Column(String(64), nullable=False)
    forecast_type = Column(String(64), nullable=False)
    predicted_value = Column(Float, nullable=False)
    unit = Column(String(32), nullable=False)
    summary = Column(Text, nullable=False)
    confidence_score = Column(Float, default=0.85)
    generated_at = Column(DateTime(timezone=True), default=_now)


class SimulationModel(Base):
    __tablename__ = "intelligence_simulations"

    simulation_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    scenario = Column(String(64), nullable=False)
    target_resource_id = Column(String(64), nullable=False)
    outcome_json = Column(JSON, default=dict)
    confidence_score = Column(Float, default=0.90)
    created_at = Column(DateTime(timezone=True), default=_now)


class DecisionModel(Base):
    __tablename__ = "intelligence_decisions"

    decision_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    status = Column(String(64), nullable=False)
    selected_option_json = Column(JSON, nullable=True)
    snapshot_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now)


class RecommendationModel(Base):
    __tablename__ = "intelligence_recommendations"

    recommendation_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    idempotency_key = Column(String(128), nullable=False, index=True)
    recommendation_type = Column(String(64), nullable=False)
    priority = Column(String(32), nullable=False)
    status = Column(String(64), nullable=False)
    title = Column(String(255), nullable=False)
    action_description = Column(Text, nullable=False)
    target_resource_id = Column(String(64), nullable=False)
    confidence_score = Column(Float, default=0.90)
    risk_level = Column(String(32), default="LOW")
    created_at = Column(DateTime(timezone=True), default=_now)
    expires_at = Column(DateTime(timezone=True), nullable=False)


class DecisionOutcomeModel(Base):
    __tablename__ = "intelligence_outcomes"

    measurement_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    recommendation_id = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False)
    cost_impact_usd = Column(Float, default=0.0)
    risk_change_pct = Column(Float, default=0.0)
    measured_at = Column(DateTime(timezone=True), default=_now)
