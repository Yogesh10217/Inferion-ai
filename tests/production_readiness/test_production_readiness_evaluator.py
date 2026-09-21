from __future__ import annotations

from app.deployment.configuration import RuntimeConfigurationManager
from app.deployment.models import ProductionReleaseDecision
from app.deployment.production_readiness import ProductionReadinessEvaluator


def test_production_readiness_success_path(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "STAGING")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://sim_user:sim_pass@localhost:5432/test_db")
    monkeypatch.setenv("JWT_SECRET", "super-strong-jwt-secret-key-production-ready-998822")

    config_mgr = RuntimeConfigurationManager()
    evaluator = ProductionReadinessEvaluator(config_manager=config_mgr)
    result = evaluator.evaluate_production_readiness()

    assert result.readiness_status in ("READY", "MANUAL_REVIEW_REQUIRED")
    assert result.release_decision in (ProductionReleaseDecision.GO, ProductionReleaseDecision.MANUAL_REVIEW_REQUIRED)
    assert len(result.blocking_reasons) == 0


def test_debug_true_blocks_production_release(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "PRODUCTION")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://sim_user:sim_pass@localhost:5432/test_db")
    monkeypatch.setenv("JWT_SECRET", "super-strong-jwt-secret-key-production-ready-998822")

    config_mgr = RuntimeConfigurationManager()
    evaluator = ProductionReadinessEvaluator(config_manager=config_mgr)
    result = evaluator.evaluate_production_readiness()

    assert result.readiness_status == "BLOCKED"
    assert result.release_decision == ProductionReleaseDecision.NO_GO
    assert any("Debug mode enabled in PRODUCTION" in err for err in result.blocking_reasons)


def test_missing_database_url_blocks_release(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "PRODUCTION")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setenv("JWT_SECRET", "super-strong-jwt-secret-key-production-ready-998822")

    config_mgr = RuntimeConfigurationManager()
    evaluator = ProductionReadinessEvaluator(config_manager=config_mgr)
    result = evaluator.evaluate_production_readiness()

    assert result.readiness_status == "BLOCKED"
    assert result.release_decision == ProductionReleaseDecision.NO_GO
    assert any("Missing database_url" in err or "database" in err.lower() for err in result.blocking_reasons)


def test_canary_secret_blocks_release(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "PRODUCTION")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://sim_user:sim_pass@localhost:5432/test_db")
    monkeypatch.setenv("JWT_SECRET", "change_me")

    config_mgr = RuntimeConfigurationManager()
    evaluator = ProductionReadinessEvaluator(config_manager=config_mgr)
    result = evaluator.evaluate_production_readiness()

    assert result.readiness_status == "BLOCKED"
    assert result.release_decision == ProductionReleaseDecision.NO_GO
    assert any("Unsafe fallback or canary secret" in err or "SECRET" in err for err in result.blocking_reasons)
