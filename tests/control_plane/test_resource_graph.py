"""Unit tests for ResourceGraph."""

import pytest
from app.control_plane.resource_graph import ResourceGraph
from app.control_plane.exceptions import ConfigurationConflictException, LifecycleException


def test_dependency_graph_and_impact_analysis():
    graph = ResourceGraph()
    graph.register_dependency("wf_1", "agent_1")
    graph.register_dependency("agent_1", "tool_1")

    # Cycle detection
    with pytest.raises(ConfigurationConflictException):
        graph.register_dependency("tool_1", "wf_1")

    # Impact analysis
    impact = graph.analyze_impact("tool_1")
    assert impact["total_impacted_resources"] == 2
    assert "agent_1" in impact["impacted_resource_ids"]
    assert "wf_1" in impact["impacted_resource_ids"]

    # Deletion safety fails when dependents exist
    with pytest.raises(LifecycleException):
        graph.validate_deletion_safety("tool_1")
