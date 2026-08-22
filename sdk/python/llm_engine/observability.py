"""Observability Python SDK Client."""

from typing import Dict, Any, List, Optional
import httpx


class ObservabilityClient:
    """Python SDK Client for Enterprise AI Observability, Monitoring & AIOps Platform."""

    def __init__(self, client: httpx.Client, base_url: str):
        self._client = client
        self.base_url = base_url

    def get_trace(self, trace_id: str) -> Dict[str, Any]:
        """Retrieve trace details by ID."""
        resp = self._client.get(f"{self.base_url}/v1/observability/traces/{trace_id}")
        resp.raise_for_status()
        return resp.json()

    def get_execution(self, execution_id: str) -> Dict[str, Any]:
        """Retrieve execution trace by ID."""
        resp = self._client.get(f"{self.base_url}/v1/observability/executions/{execution_id}")
        resp.raise_for_status()
        return resp.json()

    def get_execution_timeline(self, execution_id: str) -> Dict[str, Any]:
        """Retrieve execution timeline graph."""
        resp = self._client.get(f"{self.base_url}/v1/observability/executions/{execution_id}/timeline")
        resp.raise_for_status()
        return resp.json()

    def replay(self, execution_id: str, force_external_effects: bool = False) -> Dict[str, Any]:
        """Replay an execution with optional side effects."""
        resp = self._client.post(
            f"{self.base_url}/v1/observability/executions/{execution_id}/replay",
            json={"force_external_effects": force_external_effects},
        )
        resp.raise_for_status()
        return resp.json()

    def get_costs(
        self,
        execution_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Retrieve cost metrics."""
        params = {}
        if execution_id:
            params["execution_id"] = execution_id
        if agent_id:
            params["agent_id"] = agent_id
        if workflow_id:
            params["workflow_id"] = workflow_id
        resp = self._client.get(f"{self.base_url}/v1/observability/costs", params=params)
        resp.raise_for_status()
        return resp.json()

    def get_cost_breakdown(self) -> Dict[str, Any]:
        """Retrieve multi-level cost attribution breakdown."""
        resp = self._client.get(f"{self.base_url}/v1/observability/costs/breakdown")
        resp.raise_for_status()
        return resp.json()

    def get_performance(self, component: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve latency percentiles and performance metrics."""
        params = {"component": component} if component else {}
        resp = self._client.get(f"{self.base_url}/v1/observability/performance", params=params)
        resp.raise_for_status()
        return resp.json()

    def get_failures(self, execution_id: str) -> Dict[str, Any]:
        """Perform failure root-cause analysis."""
        resp = self._client.get(f"{self.base_url}/v1/observability/failures", params={"execution_id": execution_id})
        resp.raise_for_status()
        return resp.json()

    def get_anomalies(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent anomaly events."""
        resp = self._client.get(f"{self.base_url}/v1/observability/anomalies", params={"limit": limit})
        resp.raise_for_status()
        return resp.json()

    def get_alerts(self, status: Optional[str] = None, level: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve system alerts."""
        params = {}
        if status:
            params["status"] = status
        if level:
            params["level"] = level
        resp = self._client.get(f"{self.base_url}/v1/observability/alerts", params=params)
        resp.raise_for_status()
        return resp.json()

    def acknowledge_alert(self, alert_id: str, user_id: str = "system") -> Dict[str, Any]:
        """Acknowledge a system alert."""
        resp = self._client.post(f"{self.base_url}/v1/observability/alerts/{alert_id}/acknowledge", json={"user_id": user_id})
        resp.raise_for_status()
        return resp.json()

    def get_slos(self) -> List[Dict[str, Any]]:
        """Retrieve SLO statuses."""
        resp = self._client.get(f"{self.base_url}/v1/observability/slos")
        resp.raise_for_status()
        return resp.json()

    def get_evaluations(self) -> List[Dict[str, Any]]:
        """Retrieve Quality and Evaluation scores."""
        resp = self._client.get(f"{self.base_url}/v1/observability/evaluations")
        resp.raise_for_status()
        return resp.json()

    def get_status(self) -> Dict[str, Any]:
        """Retrieve operational status."""
        resp = self._client.get(f"{self.base_url}/v1/operations/status")
        resp.raise_for_status()
        return resp.json()

    def get_dashboard(self) -> Dict[str, Any]:
        """Retrieve AIOps operations dashboard payload."""
        resp = self._client.get(f"{self.base_url}/v1/operations/dashboard")
        resp.raise_for_status()
        return resp.json()
