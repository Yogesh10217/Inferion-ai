import os
from app.deployment.models import MigrationSafetyStatus
from app.deployment.release_validation import DeploymentReleaseValidator


def test_database_migration_safety_status():
    validator = DeploymentReleaseValidator()
    result = validator.validate_release_readiness()
    
    assert result.migration_safety_status in (
        MigrationSafetyStatus.MIGRATION_RUNTIME_NOT_EXECUTED,
        MigrationSafetyStatus.MIGRATION_SYSTEM_NOT_CONFIGURED,
    )
    assert result.migration_safety_status != MigrationSafetyStatus.MIGRATION_CONFIGURATION_VALIDATED

