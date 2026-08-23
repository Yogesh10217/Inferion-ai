"""Python SDK Client for Architecture & Digital Twin Platform (Phase 5.26)."""

from typing import Dict, Any, Optional, List


class ArchitectureClient:
    """Client for Architecture Platform REST API."""

    def __init__(self, client) -> None:
        self.client = client

    def create_node(self, name: str, node_type: str, environment: str = "production", attributes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Register an architecture node."""
        payload = {
            "name": name,
            "node_type": node_type,
            "environment": environment,
            "attributes": attributes or {},
        }
        return self.client._request("POST", "/v1/architecture/nodes", json=payload)

    def list_nodes(self, environment: Optional[str] = None) -> List[Dict[str, Any]]:
        """List architecture nodes."""
        params = {}
        if environment:
            params["environment"] = environment
        return self.client._request("GET", "/v1/architecture/nodes", params=params)

    def add_dependency(self, source_node_id: str, target_node_id: str, dependency_type: str = "DEPENDS_ON") -> Dict[str, Any]:
        """Add directed dependency."""
        payload = {
            "source_node_id": source_node_id,
            "target_node_id": target_node_id,
            "dependency_type": dependency_type,
        }
        return self.client._request("POST", "/v1/architecture/dependencies", json=payload)

    def get_topology(self, environment: str = "production") -> Dict[str, Any]:
        """Get topology graph."""
        return self.client._request("GET", "/v1/architecture/topology", params={"environment": environment})

    def create_snapshot(self, environment: str = "production", description: str = "Snapshot") -> Dict[str, Any]:
        """Create immutable snapshot."""
        payload = {"environment": environment, "description": description}
        return self.client._request("POST", "/v1/architecture/snapshots", json=payload)

    def propose_change(self, idempotency_key: str, action_type: str, target_node_ids: List[str]) -> Dict[str, Any]:
        """Propose architecture change."""
        payload = {
            "idempotency_key": idempotency_key,
            "action_type": action_type,
            "target_node_ids": target_node_ids,
        }
        return self.client._request("POST", "/v1/architecture/changes", json=payload)

    def get_drift(self) -> List[Dict[str, Any]]:
        """List architecture drifts."""
        return self.client._request("GET", "/v1/architecture/drift")

    def get_trust(self) -> Dict[str, Any]:
        """Get tenant Architecture Trust Score."""
        return self.client._request("GET", "/v1/architecture/trust")

    def get_analytics(self) -> Dict[str, Any]:
        """Get architecture analytics report."""
        return self.client._request("GET", "/v1/architecture/analytics")
