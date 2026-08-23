"""Python SDK Client for Enterprise AI Decision Intelligence Platform (Phase 5.29)."""

from typing import Dict, Any, Optional, List


class DecisionsClient:
    """Client for Decision Intelligence Platform REST API."""

    def __init__(self, client) -> None:
        self.client = client

    def create_context(self, title: str, description: str) -> Dict[str, Any]:
        """Create decision context."""
        payload = {"title": title, "description": description}
        return self.client._request("POST", "/v1/decisions/context", json=payload)

    def create_scenario(self, context_id: str, title: str, scenario_type: str = "BASELINE") -> Dict[str, Any]:
        """Create and simulate decision scenario."""
        payload = {"context_id": context_id, "title": title, "scenario_type": scenario_type}
        return self.client._request("POST", "/v1/decisions/scenarios", json=payload)

    def analyze(self, title: str) -> Dict[str, Any]:
        """Run full end-to-end decision flow analysis."""
        payload = {"title": title}
        return self.client._request("POST", "/v1/decisions/analyze", json=payload)

    def get_decision(self, decision_id: str) -> Dict[str, Any]:
        """Get decision details by ID."""
        return self.client._request("GET", f"/v1/decisions/{decision_id}")

    def finalize_decision(self, decision_id: str) -> Dict[str, Any]:
        """Finalize decision and freeze immutable snapshot."""
        return self.client._request("POST", f"/v1/decisions/{decision_id}/finalize")

    def get_analytics(self) -> Dict[str, Any]:
        """Get decision analytics report."""
        return self.client._request("GET", "/v1/decisions/analytics")
