"""Python SDK Client for Enterprise AI Knowledge Intelligence Platform (Phase 5.35)."""

from typing import Dict, Any, Optional, List


class KnowledgeIntelligenceClient:
    """Client interface for interacting with the Knowledge Intelligence Platform API."""

    def __init__(self, client: Any) -> None:
        self.client = client

    def create_item(
        self,
        tenant_id: str,
        title: str,
        knowledge_type: str = "DOCUMENT",
        classification: str = "INTERNAL",
        source_system: str = "INTERNAL",
        external_id: str = "",
        tags: Optional[List[str]] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "title": title,
            "knowledge_type": knowledge_type,
            "classification": classification,
            "source_system": source_system,
            "external_id": external_id,
            "tags": tags or [],
            "attributes": attributes or {},
        }
        return self.client.post(f"/v1/knowledge/items?tenant_id={tenant_id}", json=payload)

    def list_items(self, tenant_id: str) -> Dict[str, Any]:
        return self.client.get(f"/v1/knowledge/items?tenant_id={tenant_id}")

    def get_item(self, item_id: str, tenant_id: str) -> Dict[str, Any]:
        return self.client.get(f"/v1/knowledge/items/{item_id}?tenant_id={tenant_id}")

    def get_provenance(self, target_id: str, tenant_id: str) -> Dict[str, Any]:
        return self.client.get(f"/v1/knowledge/provenance?target_id={target_id}&tenant_id={tenant_id}")

    def get_graph(self, start_node_id: str, tenant_id: str, depth: int = 2) -> Dict[str, Any]:
        return self.client.get(f"/v1/knowledge/graph?start_node_id={start_node_id}&tenant_id={tenant_id}&depth={depth}")

    def retrieve(self, tenant_id: str, query: str) -> Dict[str, Any]:
        return self.client.post(f"/v1/knowledge/retrieval?tenant_id={tenant_id}", json={"query": query})

    def assemble_context(self, tenant_id: str, item_ids: List[str]) -> Dict[str, Any]:
        return self.client.post(f"/v1/knowledge/context?tenant_id={tenant_id}", json={"item_ids": item_ids})

    def list_contradictions(self, tenant_id: str) -> Dict[str, Any]:
        return self.client.get(f"/v1/knowledge/contradictions?tenant_id={tenant_id}")

    def get_analytics(self, tenant_id: str) -> Dict[str, Any]:
        return self.client.get(f"/v1/knowledge/analytics?tenant_id={tenant_id}")
