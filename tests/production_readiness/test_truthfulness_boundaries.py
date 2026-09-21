from __future__ import annotations

from app.deployment.production_release_report import ProductionReleaseReportGenerator


def test_truthfulness_boundaries_matrix():
    report = ProductionReleaseReportGenerator.generate_report()
    matrix = report.truthfulness_matrix

    assert matrix["PRODUCTION_DEPLOYED"] == "NOT_EXECUTED"
    assert matrix["PRODUCTION_DEPLOYMENT_VALIDATED"] == "NOT_EXECUTED"
    assert matrix["PRODUCTION_RUNTIME_VALIDATED"] == "NOT_EXECUTED"
    assert matrix["LIVE_PRODUCTION_VALIDATED"] == "NOT_EXECUTED"
    assert matrix["LIVE_PRODUCTION"] == "NOT_EXECUTED"
    assert matrix["PRODUCTION_DATABASE_MIGRATION_EXECUTED"] == "NOT_EXECUTED"
    assert matrix["PRODUCTION_BACKUP_EXECUTED"] == "NOT_EXECUTED"
    assert matrix["PRODUCTION_RESTORE_EXECUTED"] == "NOT_EXECUTED"
    assert matrix["PRODUCTION_ROLLBACK_EXECUTED"] == "NOT_EXECUTED"
    assert matrix["PRODUCTION_SMOKE_TEST_EXECUTED"] == "NOT_EXECUTED"
