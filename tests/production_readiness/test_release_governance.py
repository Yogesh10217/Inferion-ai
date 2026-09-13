from __future__ import annotations

import pytest
from app.deployment.configuration import RuntimeConfigurationManager
from app.deployment.models import PlatformReadinessClassification, ProductionReleaseDecision
from app.deployment.release_governance import ProductionReleaseDecisionEngine


def test_release_governance_decision_go(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "STAGING")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://sim_user:sim_pass@localhost:5432/test_db")
    monkeypatch.setenv("JWT_SECRET", "super-strong-jwt-secret-key-production-ready-998822")

    engine = ProductionReleaseDecisionEngine()
    result = engine.evaluate_release_decision()

    assert result.decision in (ProductionReleaseDecision.GO, ProductionReleaseDecision.MANUAL_REVIEW_REQUIRED)
    if result.decision == ProductionReleaseDecision.GO:
        assert result.status_classification == PlatformReadinessClassification.PRODUCTION_RELEASE_APPROVED
        assert result.approval_granted is True
        assert "GO FOR CONTROLLED PRODUCTION RELEASE" in result.governance_message


def test_release_governance_decision_block_on_error(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "PRODUCTION")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://sim_user:sim_pass@localhost:5432/test_db")
    monkeypatch.setenv("JWT_SECRET", "super-strong-jwt-secret-key-production-ready-998822")

    engine = ProductionReleaseDecisionEngine()
    result = engine.evaluate_release_decision()

    assert result.decision == ProductionReleaseDecision.NO_GO
    assert result.status_classification == PlatformReadinessClassification.RUNTIME_BLOCKED
    assert result.approval_granted is False
    assert len(result.blocking_reasons) > 0
