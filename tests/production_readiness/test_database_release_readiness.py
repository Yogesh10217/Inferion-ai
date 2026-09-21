from __future__ import annotations

from app.deployment.configuration import RuntimeConfigurationManager
from app.deployment.database_readiness import DatabaseReleaseReadinessEvaluator


def test_database_release_readiness_valid(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "STAGING")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://sim_user:sim_pass@localhost:5432/test_db")

    config = RuntimeConfigurationManager().get_config()
    res = DatabaseReleaseReadinessEvaluator.evaluate_database_readiness(config)

    assert res.status == "READY"
    assert res.configuration_ready is True
    assert "DATABASE_RELEASE_READY" in res.classifications
    assert "DATABASE_RUNTIME_NOT_EXECUTED" in res.classifications
    assert "MIGRATION_RUNTIME_NOT_EXECUTED" in res.classifications


def test_database_migration_not_fabricated(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "PRODUCTION")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://sim_user:sim_pass@localhost:5432/test_db")

    config = RuntimeConfigurationManager().get_config()
    res = DatabaseReleaseReadinessEvaluator.evaluate_database_readiness(config)

    # Must explicitly state MIGRATION_RUNTIME_NOT_EXECUTED and never claim production migration execution
    assert "MIGRATION_RUNTIME_NOT_EXECUTED" in res.classifications
    assert "PRODUCTION_DATABASE_MIGRATION_EXECUTED" not in res.classifications
