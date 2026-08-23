"""Unit tests for Multi-Objective Constrained Optimization Engine."""

import pytest
from app.intelligence_platform.optimization import OptimizationEngine, OptimizationObjective, OptimizationCandidate, OptimizationConstraint, ParetoOptimizationSolver


def test_optimization_solver_with_constraints():
    engine = OptimizationEngine(solver=ParetoOptimizationSolver())

    candA = OptimizationCandidate(name="High Cost Low Latency", action_type="SCALE", target_resource_id="svc_1", cost_usd=100.0, latency_ms=50.0, risk_level="LOW")
    candB = OptimizationCandidate(name="Low Cost Med Latency", action_type="MODEL_SWITCH", target_resource_id="svc_1", cost_usd=20.0, latency_ms=120.0, risk_level="LOW")

    # Constraint max cost $30
    constraint = OptimizationConstraint(max_cost_usd=30.0)
    res = engine.optimize("t1", OptimizationObjective.MINIMIZE_COST, [candA, candB], constraint)

    assert res.winning_candidate.name == "Low Cost Med Latency"
    assert res.solver_name == "ParetoOptimizationSolver"
