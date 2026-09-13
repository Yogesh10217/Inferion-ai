"""
Tests for Security Metrics Calculator (Phase 5.69).
"""

import pytest
from app.security_operations.vulnerability_management import VulnerabilityManager
from app.security_operations.security_metrics import SecurityMetricsCalculator, SecurityMetricsResult


def test_security_metrics_calculation():
    vuln_mgr = VulnerabilityManager()
    vuln_mgr.add_vulnerability("CVE-1", "V1", "CRITICAL", "comp1", "desc")
    vuln_mgr.add_vulnerability("CVE-2", "V2", "HIGH", "comp2", "desc")
    assessment = vuln_mgr.assess_vulnerabilities()

    calc = SecurityMetricsCalculator()
    metrics = calc.calculate_metrics(
        posture_score=85.0,
        vulnerability_assessment=assessment,
        active_exceptions_count=1,
        compliance_score=92.0,
        is_production=False,
    )

    assert isinstance(metrics, SecurityMetricsResult)
    assert 0.0 <= metrics.posture_index <= 100.0
    assert metrics.vulnerability_density >= 0.0
    assert 0.0 <= metrics.patch_compliance_rate <= 100.0
    assert metrics.fingerprint.startswith("sha256:")
