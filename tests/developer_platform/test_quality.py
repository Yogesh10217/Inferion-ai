"""Unit tests for QualityManager."""

import pytest

from app.developer_platform.exceptions import QualityGateViolationException
from app.developer_platform.quality import QualityGate, QualityManager


def test_quality_gate_evaluation():
    qm = QualityManager()
    gate = QualityGate(min_coverage_pct=85.0, max_critical_bugs=0)

    # Coverage 90%, 0 bugs -> PASSED
    assert qm.evaluate_quality(gate, coverage_pct=90.0, critical_bugs=0) is True

    # Coverage 75% -> FAILS gate
    with pytest.raises(QualityGateViolationException):
        qm.evaluate_quality(gate, coverage_pct=75.0, critical_bugs=0)
