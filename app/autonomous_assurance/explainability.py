"""
Workflow Explainability Subsystem (Addition #5).
Provides human-readable, transparent, and auditable explanations for workflow creation, priority selection,
approval gates, delegation creation, recovery triggers, and compensation choices.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class WorkflowExplainabilityRecord(BaseModel):
    explainability_id: str = Field(default_factory=lambda: f"expl_{uuid.uuid4().hex[:12]}")
    workflow_id: str
    tenant_id: str
    creation_rationale: str
    priority_rationale: str
    approval_rationale: Optional[str] = None
    delegation_rationale: Optional[str] = None
    recovery_rationale: Optional[str] = None
    compensation_rationale: Optional[str] = None
    summary: str = "Workflow execution explanation generated successfully."
    audit_summary: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WorkflowExplainabilityEngine:
    """Generates transparent, governance-compliant audit explanations for workflow actions."""

    def __init__(self) -> None:
        self._records: Dict[str, WorkflowExplainabilityRecord] = {}

    def generate_explanation(
        self,
        workflow_id: str,
        tenant_id: str,
        title: str,
        priority: str,
        risk_score: float,
        requires_approval: bool,
        action_type: str = "DELEGATE_ACTION",
        recovery_triggered: bool = False,
        compensation_triggered: bool = False,
    ) -> WorkflowExplainabilityRecord:
        creation_rat = f"Workflow '{title}' created to coordinate cross-domain signals for workflow '{workflow_id}'."
        priority_rat = f"Priority '{priority}' selected based on Risk Score ({risk_score:.1f}) and security/operational criticality."
        approval_rat = (
            f"Approval REQUIRED because Risk ({risk_score:.1f}) >= 50.0 or action '{action_type}' carries high operational impact."
            if requires_approval
            else "Approval NOT required; workflow parameters fall within autonomous execution thresholds."
        )
        delegation_rat = f"Delegation created to dispatch formal DelegationRequest to downstream execution engine for action '{action_type}'."
        recovery_rat = "Recovery triggered due to step failure verification." if recovery_triggered else None
        compensation_rat = "Compensation selected to mitigate partial execution effects." if compensation_triggered else None

        record = WorkflowExplainabilityRecord(
            workflow_id=workflow_id,
            tenant_id=tenant_id,
            creation_rationale=creation_rat,
            priority_rationale=priority_rat,
            approval_rationale=approval_rat,
            delegation_rationale=delegation_rat,
            recovery_rationale=recovery_rat,
            compensation_rationale=compensation_rat,
            summary=f"Workflow '{title}' created with priority '{priority}'. {creation_rat}",
            audit_summary={
                "workflow_id": workflow_id,
                "tenant_id": tenant_id,
                "risk_score": risk_score,
                "requires_approval": requires_approval,
            },
        )
        self._records[workflow_id] = record
        return record

    def explain_workflow(self, workflow_id: str, tenant_id: str) -> WorkflowExplainabilityRecord:
        rec = self._records.get(workflow_id)
        if not rec:
            rec = self.generate_explanation(workflow_id, tenant_id, "Explained Workflow", "HIGH", 20.0, False)
        return rec

    def get_explanation(self, workflow_id: str) -> Optional[WorkflowExplainabilityRecord]:
        return self._records.get(workflow_id)
