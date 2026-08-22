"""Unit tests for DependencyManager."""

import pytest
from app.developer_platform.dependency_intelligence import DependencyManager
from app.developer_platform.exceptions import DependencyRiskViolationException


def test_dependency_vulnerability_risk_detection():
    dm = DependencyManager()
    deps = [
        {"name": "requests", "version": "2.31.0", "risk_level": "LOW"},
        {"name": "vulnerable-lib", "version": "1.0.0", "risk_level": "CRITICAL"},
    ]

    with pytest.raises(DependencyRiskViolationException):
        dm.analyze_dependencies(deps, tenant_id="t_dep")
