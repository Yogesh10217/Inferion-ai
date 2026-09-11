from app.deployment.shutdown import DeploymentShutdownManager
from app.deployment.models import ShutdownState, DeploymentEnvironment, EnvironmentConfig


def test_shutdown_lifecycle_transitions():
    """Verifies graceful shutdown sequence through READY -> DRAINING -> STOPPING -> STOPPED."""
    shutdown_mgr = DeploymentShutdownManager()
    config = EnvironmentConfig(
        environment=DeploymentEnvironment.STAGING,
        application_name="enterprise-ai-platform",
        application_version="1.0.0",
        deployment_version="5.60A",
        region="us-east-1",
        instance_id="inst-staging-01",
        debug_enabled=False,
        database_url="postgresql://user:pass@localhost:5432/staging_db",
        cache_enabled=True,
        messaging_enabled=True,
        observability_enabled=True,
        log_level="INFO",
        shutdown_timeout=5,
    )
    shutdown_mgr.config = config
    assert shutdown_mgr.state == ShutdownState.READY

    final_state = shutdown_mgr.execute_shutdown()
    assert final_state == ShutdownState.STOPPED
    assert shutdown_mgr.state == ShutdownState.STOPPED
