"""
Tests for Workflow Graph & DAG Structure Validation
"""

import pytest

from app.workflows.dag import DAGBuilder
from app.workflows.edge import Edge
from app.workflows.exceptions import GraphValidationError
from app.workflows.graph import WorkflowGraph
from app.workflows.node import AgentNode, EndNode, StartNode


def test_valid_dag_construction():
    graph = WorkflowGraph("g1")
    start = StartNode()
    agent = AgentNode("a1", "Agent 1", agent_id="agent_1")
    end = EndNode()

    graph.add_node(start)
    graph.add_node(agent)
    graph.add_node(end)

    graph.add_edge(Edge("START", "a1"))
    graph.add_edge(Edge("a1", "END"))

    graph.validate()
    order = graph.get_topological_order()
    assert order == ["START", "a1", "END"]


def test_cycle_detection_raises_error():
    graph = WorkflowGraph("g_cycle")
    start = StartNode()
    a1 = AgentNode("a1", "Agent 1", agent_id="agent_1")
    a2 = AgentNode("a2", "Agent 2", agent_id="agent_2")
    end = EndNode()

    graph.add_node(start)
    graph.add_node(a1)
    graph.add_node(a2)
    graph.add_node(end)

    graph.add_edge(Edge("START", "a1"))
    graph.add_edge(Edge("a1", "a2"))
    graph.add_edge(Edge("a2", "a1"))  # Cycle: a1 -> a2 -> a1
    graph.add_edge(Edge("a2", "END"))

    with pytest.raises(GraphValidationError, match="contains cycles"):
        graph.validate()


def test_dag_builder_utility():
    builder = DAGBuilder("g_builder")
    graph = (
        builder.add_start()
        .add_agent("a1", "Research", agent_id="research_agent")
        .add_tool("t1", "Fetch Data", tool_name="fetcher")
        .add_end()
        .connect("START", "a1")
        .connect("a1", "t1")
        .connect("t1", "END")
        .build()
    )
    assert len(graph.nodes) == 4
    assert graph.get_topological_order() == ["START", "a1", "t1", "END"]
