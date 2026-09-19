"""
Prometheus Metrics Declarations for Autonomous Planning Platform
"""

from prometheus_client import Counter, Gauge, Histogram

plans_created_total = Counter("plans_created_total", "Total number of execution plans created", ["tenant_id"])

plans_completed_total = Counter("plans_completed_total", "Total number of plans completed successfully", ["tenant_id"])

plans_failed_total = Counter("plans_failed_total", "Total number of plans failed", ["tenant_id", "error_type"])

plan_duration_seconds = Histogram(
    "plan_duration_seconds",
    "Duration of plan execution in seconds",
    ["tenant_id"],
    buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 300.0],
)

plan_cost_total = Counter("plan_cost_total", "Total dollar cost incurred by plan executions", ["tenant_id"])

planning_confidence_score = Gauge(
    "planning_confidence_score", "Confidence score gauge for generated plans", ["plan_id"]
)

simulations_run_total = Counter("simulations_run_total", "Total plan simulations run", ["tenant_id"])

reflections_generated_total = Counter(
    "reflections_generated_total", "Total reflection analyses performed", ["tenant_id"]
)

lessons_learned_total = Counter(
    "lessons_learned_total", "Total lessons extracted from execution episodes", ["tenant_id"]
)

optimization_recommendations_total = Counter(
    "optimization_recommendations_total", "Total optimization recommendations produced", ["tenant_id"]
)
