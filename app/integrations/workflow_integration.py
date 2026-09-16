"""Workflow Integration Adapter."""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class WorkflowIntegrationAdapter:
    """Allows workflow engines to invoke external integration connectors."""

    def invoke_connector_step(self, workflow_id: str, connector_name: str, action: str, tenant_id: str = "global") -> Dict[str, Any]:
        logger.info(f"[WORKFLOW INTEGRATION ADAPTER] Workflow '{workflow_id}' invoked connector '{connector_name}' action '{action}'")
        return {"status": "SUCCESS", "workflow_id": workflow_id, "connector": connector_name, "action": action}
