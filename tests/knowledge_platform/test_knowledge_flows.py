"""Mandatory End-to-End Integration Flow Tests for Phase 5.19 Knowledge Platform."""

import pytest
from app.knowledge_platform.manager import KnowledgePlatformManager
from app.knowledge_platform.knowledge import KnowledgeType, KnowledgeStatus
from app.knowledge_platform.retrieval import RetrievalRequest, RetrievalStrategy
from app.knowledge_platform.context import ContextStrategy
from app.knowledge_platform.compression import CompressionStrategy
from app.knowledge_platform.memory import MemoryType, MemoryScope
from app.knowledge_platform.knowledge_graph import KnowledgeNodeType, KnowledgeRelationship
from app.knowledge_platform.freshness import StalenessReason
from app.knowledge_platform.conflicts import ConflictType, ConflictResolutionStrategy
from app.knowledge_platform.exceptions import KnowledgeAccessDeniedException


def test_flow_1_governed_enterprise_retrieval():
    """FLOW 1 — Governed Enterprise Retrieval: Identity validation, pre-retrieval authorization, and citation generation."""
    mgr = KnowledgePlatformManager()

    # 1. Store knowledge items
    item1 = mgr.create_and_index_knowledge("Standard Operating Procedure", content="Public SOP", classification="INTERNAL", tenant_id="t_kf1")
    item2 = mgr.create_and_index_knowledge("Secret Financial Model", content="Restricted revenue forecasts", classification="RESTRICTED", tenant_id="t_kf1")

    # 2. Viewer role retrieves -> Restricted item filtered out BEFORE ranking/context!
    req = RetrievalRequest(query="SOP revenue", tenant_id="t_kf1", identity_id="user_viewer", user_role="viewer")
    res = mgr.retrieval_pipeline.execute_retrieval(req)

    assert len(res.items) == 1
    assert res.items[0]["item_id"] == item1.item_id
    assert res.citations[0]["source_id"] == item1.item_id


def test_flow_2_agent_memory_isolation():
    """FLOW 2 — Agent Memory Isolation: Strict private scope access prevention."""
    mgr = KnowledgePlatformManager()

    # Agent A stores private memory
    mem = mgr.memory_manager.store_memory(
        key="alpha_strategy",
        value="Secret Plan Alpha",
        memory_type=MemoryType.AGENT,
        scope=MemoryScope.AGENT,
        owner_agent_id="agent_alpha",
        tenant_id="t_kf2",
    )

    # Agent A retrieves own memory -> Allowed
    mem_alpha = mgr.memory_manager.get_memory(mem.memory_id, requesting_agent_id="agent_alpha")
    assert mem_alpha.value == "Secret Plan Alpha"

    # Agent B attempts retrieval -> Access Denied Exception!
    with pytest.raises(KnowledgeAccessDeniedException):
        mgr.memory_manager.get_memory(mem.memory_id, requesting_agent_id="agent_beta")


def test_flow_3_stale_knowledge_detection():
    """FLOW 3 — Stale Knowledge Detection: Data Fabric CDC event triggers status change."""
    mgr = KnowledgePlatformManager()
    item = mgr.create_and_index_knowledge("Postgres Schema Doc", content="V1 schema", tenant_id="t_kf3")
    item.source_id = "src_pg_100"

    # CDC Event emitted from Data Fabric
    stale_ids = mgr.freshness_evaluator.process_cdc_event("src_pg_100", tenant_id="t_kf3", reason=StalenessReason.SOURCE_CHANGED)
    assert item.item_id in stale_ids

    # Item status is now STALE
    upd_item = mgr.knowledge_manager.get_item(item.item_id)
    assert upd_item.status == KnowledgeStatus.STALE


def test_flow_4_knowledge_conflict():
    """FLOW 4 — Knowledge Conflict: Conflicting sources preserved and resolved deterministically."""
    mgr = KnowledgePlatformManager()

    item_a = mgr.create_and_index_knowledge("Q3 Revenue Source A", content="15M USD", tenant_id="t_kf4")
    item_b = mgr.create_and_index_knowledge("Q3 Revenue Source B", content="18M USD", tenant_id="t_kf4")
    item_a.confidence_score = 0.95
    item_b.confidence_score = 0.80

    # Conflict detected
    cnflct = mgr.conflict_manager.detect_conflict(item_a.item_id, item_b.item_id, conflict_type=ConflictType.FACT_CONTRADICTION, tenant_id="t_kf4")

    # Resolve via CONFIDENCE
    resolved = mgr.conflict_manager.resolve_conflict(cnflct.conflict_id, strategy=ConflictResolutionStrategy.CONFIDENCE)
    assert resolved.resolved_item_id == item_a.item_id

    # Item A ACTIVE, Item B SUPERSEDED (both preserved!)
    assert mgr.knowledge_manager.get_item(item_a.item_id).status == KnowledgeStatus.ACTIVE
    assert mgr.knowledge_manager.get_item(item_b.item_id).status == KnowledgeStatus.SUPERSEDED


def test_flow_5_context_budget_optimization():
    """FLOW 5 — Context Budget Optimization: Context token compression & FinOps savings tracking."""
    mgr = KnowledgePlatformManager()

    # Large retrieval result
    item = mgr.create_and_index_knowledge("Large Text Doc", content="Word " * 500, tenant_id="t_kf5")
    ret_req = RetrievalRequest(query="Word", tenant_id="t_kf5", identity_id="user_1")
    ret_res = mgr.retrieval_pipeline.execute_retrieval(ret_req)

    # Build context window & compress
    cwin = mgr.context_builder.build_context(ret_res, strategy=ContextStrategy.RELEVANCE_FIRST, max_tokens=400)
    cmp_res = mgr.context_compressor.compress_context(cwin, strategy=CompressionStrategy.DEDUPLICATION, target_ratio=0.5)

    assert cmp_res.tokens_saved > 0
    assert cmp_res.provenance_preserved is True


def test_flow_6_multi_hop_knowledge_graph_retrieval():
    """FLOW 6 — Multi-Hop Knowledge Graph Retrieval: Entity linking & graph traversal."""
    mgr = KnowledgePlatformManager()

    # Construct Graph
    n1 = mgr.knowledge_graph_manager.add_node("Service Alpha", node_type=KnowledgeNodeType.RESOURCE, tenant_id="t_kf6")
    n2 = mgr.knowledge_graph_manager.add_node("Database Beta", node_type=KnowledgeNodeType.DATASET, tenant_id="t_kf6")
    n3 = mgr.knowledge_graph_manager.add_node("Owner Alice", node_type=KnowledgeNodeType.PERSON, tenant_id="t_kf6")

    mgr.knowledge_graph_manager.add_edge(n1.node_id, n2.node_id, relationship=KnowledgeRelationship.USES, tenant_id="t_kf6")
    mgr.knowledge_graph_manager.add_edge(n2.node_id, n3.node_id, relationship=KnowledgeRelationship.OWNED_BY, tenant_id="t_kf6")

    # Multi-hop traversal
    results = mgr.knowledge_graph_manager.multi_hop_traversal(n1.node_id, max_hops=2, tenant_id="t_kf6")
    res_ids = [n.node_id for n in results]

    assert n1.node_id in res_ids
    assert n2.node_id in res_ids
    assert n3.node_id in res_ids


def test_flow_7_agent_plus_workflow_organizational_learning():
    """FLOW 7 — Agent + Workflow Organizational Learning: Insight recording and retrieval."""
    mgr = KnowledgePlatformManager()

    # Workflow completes & records verified insight
    insight_id = mgr.workflow_adapter.record_workflow_insight("wf_prod_run_1", title="Deployment Insight", content="Postgres connection pool size 20 optimal", tenant_id="t_kf7")
    assert insight_id.startswith("kitem_")

    # Future agent retrieves this insight
    ret_res = mgr.agent_adapter.query_knowledge_for_agent("agent_optimizer", query="Postgres connection pool", tenant_id="t_kf7")
    assert len(ret_res.items) == 1
    assert ret_res.items[0]["item_id"] == insight_id


def test_flow_8_strict_cross_tenant_isolation():
    """FLOW 8 — Strict Cross-Tenant Isolation: Tenant A cannot retrieve Tenant B knowledge."""
    mgr = KnowledgePlatformManager()

    mgr.create_and_index_knowledge("Tenant A Doc", content="Secret A", tenant_id="Tenant_A")
    mgr.create_and_index_knowledge("Tenant B Doc", content="Secret B", tenant_id="Tenant_B")

    # Tenant A retrieve
    res_A = mgr.retrieval_pipeline.execute_retrieval(RetrievalRequest(query="Secret", tenant_id="Tenant_A", identity_id="user_a"))
    assert len(res_A.items) == 1
    assert res_A.items[0]["title"] == "Tenant A Doc"

    # Tenant B retrieve
    res_B = mgr.retrieval_pipeline.execute_retrieval(RetrievalRequest(query="Secret", tenant_id="Tenant_B", identity_id="user_b"))
    assert len(res_B.items) == 1
    assert res_B.items[0]["title"] == "Tenant B Doc"
