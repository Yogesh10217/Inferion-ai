"""Unit tests for KnowledgeGraphManager nodes and edges."""

from app.knowledge_platform.knowledge_graph import KnowledgeGraphManager, KnowledgeNodeType, KnowledgeRelationship


def test_knowledge_graph_node_and_edge_creation():
    graph = KnowledgeGraphManager()

    n1 = graph.add_node("Service A", node_type=KnowledgeNodeType.RESOURCE, tenant_id="t_kg")
    n2 = graph.add_node("Database B", node_type=KnowledgeNodeType.DATASET, tenant_id="t_kg")

    edge = graph.add_edge(n1.node_id, n2.node_id, relationship=KnowledgeRelationship.DEPENDS_ON, tenant_id="t_kg")

    assert edge.source_node_id == n1.node_id
    assert edge.target_node_id == n2.node_id
    assert edge.relationship == KnowledgeRelationship.DEPENDS_ON
