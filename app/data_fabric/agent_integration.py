"""Agent, Workflow & Extension Integration Subsystem."""

import logging
import uuid
from typing import Optional

from pydantic import BaseModel, Field

from app.data_fabric.data_source import DataSourceManager
from app.data_fabric.governance import DataAccessDecision, DataClassification, DataGovernanceEngine
from app.data_fabric.lineage import DataLineageManager

logger = logging.getLogger(__name__)


class DataAccessRequest(BaseModel):
    """Governed data access request submitted by Agent, Workflow, or Extension."""

    request_id: str = Field(default_factory=lambda: f"req_{uuid.uuid4().hex[:10]}")

    requester_id: str  # agent_id, workflow_id, extension_id
    tenant_id: str = "global"
    workspace_id: Optional[str] = None
    data_source_id: str
    requested_scope: str = "read"
    purpose: str = "AI Execution Context"
    execution_id: Optional[str] = None


class AgentDataFabricAdapter:
    """Brokers policy-governed data access for Agents, Teams, Workflows, Planning, Autonomy, Workers, Tools, MCP, Extensions."""

    def __init__(
        self,
        source_manager: Optional[DataSourceManager] = None,
        governance_engine: Optional[DataGovernanceEngine] = None,
        lineage_manager: Optional[DataLineageManager] = None,
    ) -> None:
        self.source_manager = source_manager or DataSourceManager()
        self.governance_engine = governance_engine or DataGovernanceEngine()
        self.lineage_manager = lineage_manager or DataLineageManager()

    def request_data_access(
        self,
        requester_id: str,
        data_source_id: str,
        tenant_id: str = "global",
        workspace_id: Optional[str] = None,
        classification: DataClassification = DataClassification.INTERNAL,
        purpose: str = "AI Agent Context Gathering",
    ) -> DataAccessDecision:
        """Process data access request: Tenant Check -> Policy Evaluation -> Approval Gate -> Lineage Link."""
        ds = self.source_manager.get_source(data_source_id)

        # Tenant isolation check
        if ds.tenant_id != tenant_id and tenant_id != "global":
            logger.warning(f"[AGENT DATA ADAPTER] Cross-tenant access blocked (Tenant '{tenant_id}' -> Source '{data_source_id}' of Tenant '{ds.tenant_id}')")
            return DataAccessDecision(permitted=False, reason="Cross-tenant access prohibited", classification=classification)

        decision = self.governance_engine.evaluate_access(
            tenant_id=tenant_id,
            resource_id=data_source_id,
            classification=classification,
            requester_id=requester_id,
            purpose=purpose,
        )

        if decision.permitted:
            # Record lineage link: Source -> Agent Execution
            self.lineage_manager.record_lineage(
                source_node_id=f"ds_{data_source_id}",
                target_node_id=f"agent_{requester_id}",
                relationship_type="ACCESSED_BY_AGENT",
            )
            logger.info(f"[AGENT DATA ADAPTER] Granted data access to '{requester_id}' for source '{ds.name}'")

        return decision
