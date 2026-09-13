"""
Tests for Availability Engine.
"""

from app.reliability.availability_engine import AvailabilityClassification, AvailabilityEvaluator


def test_availability_calculation():
    evaluator = AvailabilityEvaluator()
    res = evaluator.evaluate_availability(uptime_seconds=990.0, downtime_seconds=10.0)
    assert res.uptime_percentage == 99.0
    assert res.classification == AvailabilityClassification.HEALTHY


def test_availability_zero_division_protection():
    evaluator = AvailabilityEvaluator()
    res = evaluator.evaluate_availability(uptime_seconds=0.0, downtime_seconds=0.0)
    assert res.uptime_percentage == 0.0
    assert res.classification == AvailabilityClassification.UNKNOWN
