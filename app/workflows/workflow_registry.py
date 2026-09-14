"""
Workflow Registry for Definitions & Templates
"""

from typing import Dict, Any, List, Optional
from app.workflows.workflow import WorkflowDefinition
from app.workflows.templates import WorkflowTemplates


class WorkflowRegistry:
    """In-memory & persistent registry for Workflow Definitions and Templates."""

    def __init__(self):
        self._definitions: Dict[str, WorkflowDefinition] = {}
        self._load_templates()

    def _load_templates(self) -> None:
        """Populate built-in templates into registry."""
        templates = [
            ("tmpl_research", "Research Workflow", WorkflowTemplates.build_research_workflow()),
            ("tmpl_customer_support", "Customer Support Workflow", WorkflowTemplates.build_customer_support_workflow()),
            ("tmpl_doc_review", "Document Review Workflow", WorkflowTemplates.build_document_review_workflow()),
            ("tmpl_rag", "RAG Workflow", WorkflowTemplates.build_rag_workflow()),
            ("tmpl_data_analysis", "Data Analysis Workflow", WorkflowTemplates.build_data_analysis_workflow()),
            ("tmpl_code_gen", "Code Generation Workflow", WorkflowTemplates.build_code_generation_workflow()),
            ("tmpl_compliance", "Compliance Workflow", WorkflowTemplates.build_compliance_workflow()),
            ("tmpl_approval", "Approval Workflow", WorkflowTemplates.build_approval_workflow()),
            ("tmpl_incident_response", "Incident Response Workflow", WorkflowTemplates.build_incident_response_workflow()),
            ("tmpl_knowledge_ingestion", "Knowledge Ingestion Workflow", WorkflowTemplates.build_knowledge_ingestion_workflow()),
        ]
        for tid, name, graph in templates:
            wf = WorkflowDefinition(
                workflow_id=tid,
                name=name,
                description=f"Built-in Enterprise Template: {name}",
                graph=graph,
            )
            self._definitions[tid] = wf

    def register_workflow(self, workflow: WorkflowDefinition) -> WorkflowDefinition:
        self._definitions[workflow.workflow_id] = workflow
        return workflow

    def get_workflow(self, workflow_id: str) -> WorkflowDefinition:
        if workflow_id not in self._definitions:
            raise KeyError(f"Workflow '{workflow_id}' not found in registry")
        return self._definitions[workflow_id]

    def list_workflows(self, organization_id: Optional[str] = None) -> List[WorkflowDefinition]:
        if organization_id:
            return [
                wf for wf in self._definitions.values()
                if wf.organization_id == organization_id or wf.workflow_id.startswith("tmpl_")
            ]
        return list(self._definitions.values())

    def delete_workflow(self, workflow_id: str) -> None:
        if workflow_id in self._definitions:
            del self._definitions[workflow_id]

    def get_templates(self) -> List[Dict[str, Any]]:
        return [
            wf.to_dict() for wf in self._definitions.values()
            if wf.workflow_id.startswith("tmpl_")
        ]
