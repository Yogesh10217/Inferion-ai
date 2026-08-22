"""Unit tests for GovernanceReportGenerator audit package generation."""

import pytest
from app.governance_platform.reporting import GovernanceReportGenerator


def test_audit_package_generation():
    gen = GovernanceReportGenerator()
    pkg = gen.generate_audit_package(tenant_id="t_rep", scope="TENANT")

    assert pkg.tenant_id == "t_rep"
    assert "risk_posture" in pkg.model_dump()
    assert "compliance_posture" in pkg.model_dump()
    assert "Does NOT guarantee regulatory compliance" in pkg.disclaimer
