"""Unit tests for multi-hop graph traversal."""

from app.knowledge_platform.knowledge_graph import KnowledgeGraphManager, KnowledgeNodeType, KnowledgeRelationship


def test_multi_hop_graph_traversal():
    graph = KnowledgeGraphManager()

    n1 = graph.add_node("Root Node", node_type=KnowledgeNodeType.ENTITY, tenant_id="t_gr")
    n2 = graph.add_node("Hop 1 Node", node_type=KnowledgeNodeType.DOCUMENT, tenant_id="t_gr")
    n3 = graph.add_node("Hop 2 Node", node_type=KnowledgeNodeType.PERSON, tenant_id="t_gr")

    graph.add_edge(n1.node_id, n2.node_id, relationship=KnowledgeRelationship.RELATED_TO, tenant_id="t_gr")
    graph.add_edge(n2.node_id, n3.node_id, relationship=KnowledgeRelationship.CREATED_BY, tenant_id="t_gr")

    traversed = graph.multi_hop_traversal(n1.node_id, max_hops=2, tenant_id="t_gr")
    node_ids = [n.node_id for n in traversed]

    assert n1.node_id in node_ids
    assert n2.node_id in node_ids
    assert n3.node_id in node_ids
