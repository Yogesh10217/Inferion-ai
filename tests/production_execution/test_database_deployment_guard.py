from app.deployment.database_deployment_guard import DatabaseDeploymentGuard
from app.deployment.environment import EnvironmentManager


def test_database_guard_staging_pass(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "STAGING")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://sim_user:sim_pass@localhost:5432/test_db")
    cfg = EnvironmentManager().load_environment_config()

    res = DatabaseDeploymentGuard.evaluate_database_guard(config=cfg)
    assert res.preflight_ready is True
    assert res.status == "DATABASE_PREFLIGHT_READY"


def test_database_guard_production_requires_explicit_authorization(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "PRODUCTION")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://prod_user:prod_pass@prod-host:5432/prod_db")
    cfg = EnvironmentManager().load_environment_config()

    res_unauth = DatabaseDeploymentGuard.evaluate_database_guard(config=cfg, explicit_migration_authorized=False)
    assert res_unauth.preflight_ready is False
    assert any("DATABASE_MIGRATION_REQUIRED" in err for err in res_unauth.blocking_reasons)

    res_auth = DatabaseDeploymentGuard.evaluate_database_guard(config=cfg, explicit_migration_authorized=True)
    assert res_auth.preflight_ready is True
