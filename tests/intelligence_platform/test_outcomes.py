"""Unit tests for Outcome Measurement & Deviation Evaluator."""

import pytest
from app.intelligence_platform.outcomes import OutcomeEvaluator, OutcomeStatus


def test_outcome_measurement_and_deviation():
    evaluator = OutcomeEvaluator()
    meas = evaluator.evaluate_outcome("t1", recommendation_id="rec_100", expected_cost_impact_usd=-10.0, actual_cost_impact_usd=-15.0)

    assert meas.measurement_id.startswith("meas_")
    assert meas.status == OutcomeStatus.OUTPERFORMED
    assert len(meas.metrics) == 2
