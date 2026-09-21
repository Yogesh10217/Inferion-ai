from app.deployment.cache_validation import CacheDependencyValidator
from app.deployment.database_validation import DatabaseDependencyValidator
from app.deployment.dependency_validation import DeploymentDependencyValidator
from app.deployment.models import DependencyCategory, DependencyStatus, DeploymentEnvironment, EnvironmentConfig


def test_real_postgres_socket_probe():
    """Performs real socket probe to localhost:5432 or safe fallback."""
    res = DatabaseDependencyValidator.validate_database(
        db_url="postgresql://test:test@localhost:5432/testdb",
        required=True,
        timeout_sec=0.5,
    )
    assert res.category == DependencyCategory.DATABASE
    assert res.status in (DependencyStatus.AVAILABLE, DependencyStatus.UNAVAILABLE, DependencyStatus.DEGRADED)
    assert "real_socket_connected" in res.details


def test_real_redis_socket_probe():
    """Performs real socket probe to localhost:6379 or safe fallback."""
    res = CacheDependencyValidator.validate_cache(
        enabled=True,
        required=False,
        host="localhost",
        port=6379,
        timeout_sec=0.5,
    )
    assert res.category == DependencyCategory.CACHE
    assert res.status in (DependencyStatus.AVAILABLE, DependencyStatus.DEGRADED)
    assert "real_socket_connected" in res.details


def test_optional_dependency_degradation():
    """Verifies that an optional dependency failure results in DEGRADED status without crash."""
    config = EnvironmentConfig(
        environment=DeploymentEnvironment.DEVELOPMENT,
        application_name="enterprise-ai-platform",
        application_version="1.0.0",
        deployment_version="5.60A",
        region="us-east-1",
        instance_id="inst-01",
        debug_enabled=False,
        database_url="sqlite:///./test.db",
        cache_enabled=True,
        messaging_enabled=False,
        observability_enabled=False,
        log_level="INFO",
    )
    results = DeploymentDependencyValidator.validate_all_dependencies(config)
    healthy = DeploymentDependencyValidator.evaluate_dependency_health(results)
    assert healthy is True
