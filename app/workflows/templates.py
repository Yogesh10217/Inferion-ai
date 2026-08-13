"""
Enterprise Workflow Built-in Templates (10 Standard Patterns)
"""

from typing import Dict, Any, List
from app.workflows.dag import DAGBuilder
from app.workflows.graph import WorkflowGraph


class WorkflowTemplates:
    """Catalog of 10 Enterprise Workflow Templates."""

    @staticmethod
    def get_template_names() -> List[str]:
        return [
            "Research Workflow",
            "Customer Support Workflow",
            "Document Review Workflow",
            "RAG Workflow",
            "Data Analysis Workflow",
            "Code Generation Workflow",
            "Compliance Workflow",
            "Approval Workflow",
            "Incident Response Workflow",
            "Knowledge Ingestion Workflow",
        ]

    @staticmethod
    def build_research_workflow() -> WorkflowGraph:
        builder = DAGBuilder("tmpl_research")
        builder.add_start()
        builder.add_knowledge("k1", "Search Literature", action="search")
        builder.add_agent("a1", "Research Agent", agent_id="research_agent", role="Researcher")
        builder.add_agent("a2", "Synthesis Agent", agent_id="synth_agent", role="Writer")
        builder.add_end()

        builder.connect("START", "k1")
        builder.connect("k1", "a1")
        builder.connect("a1", "a2")
        builder.connect("a2", "END")
        return builder.build()

    @staticmethod
    def build_customer_support_workflow() -> WorkflowGraph:
        builder = DAGBuilder("tmpl_customer_support")
        builder.add_start()
        builder.add_agent("triage", "Triage Agent", agent_id="triage_agent", role="Support")
        builder.add_knowledge("kb", "Knowledge Lookup", action="search")
        builder.add_agent("response", "Response Agent", agent_id="response_agent", role="Support")
        builder.add_end()

        builder.connect("START", "triage")
        builder.connect("triage", "kb")
        builder.connect("kb", "response")
        builder.connect("response", "END")
        return builder.build()

    @staticmethod
    def build_document_review_workflow() -> WorkflowGraph:
        builder = DAGBuilder("tmpl_doc_review")
        builder.add_start()
        builder.add_tool("parser", "Parse Document", tool_name="pdf_parser")
        builder.add_agent("reviewer", "Reviewer Agent", agent_id="reviewer_agent", role="Reviewer")
        builder.add_approval("approval", "Human Approval", approver_role="legal_admin")
        builder.add_end()

        builder.connect("START", "parser")
        builder.connect("parser", "reviewer")
        builder.connect("reviewer", "approval")
        builder.connect("approval", "END")
        return builder.build()

    @staticmethod
    def build_rag_workflow() -> WorkflowGraph:
        builder = DAGBuilder("tmpl_rag")
        builder.add_start()
        builder.add_knowledge("retrieve", "Hybrid Retrieve", action="search")
        builder.add_agent("generator", "RAG Generator", agent_id="rag_agent", role="RAG")
        builder.add_end()

        builder.connect("START", "retrieve")
        builder.connect("retrieve", "generator")
        builder.connect("generator", "END")
        return builder.build()

    @staticmethod
    def build_data_analysis_workflow() -> WorkflowGraph:
        builder = DAGBuilder("tmpl_data_analysis")
        builder.add_start()
        builder.add_tool("query_db", "Query Database", tool_name="db_tool")
        builder.add_agent("analyzer", "Data Analyzer Agent", agent_id="data_agent", role="DataAnalyst")
        builder.add_end()

        builder.connect("START", "query_db")
        builder.connect("query_db", "analyzer")
        builder.connect("analyzer", "END")
        return builder.build()

    @staticmethod
    def build_code_generation_workflow() -> WorkflowGraph:
        builder = DAGBuilder("tmpl_code_gen")
        builder.add_start()
        builder.add_agent("coder", "Coding Agent", agent_id="coder_agent", role="Developer")
        builder.add_agent("qa", "QA Agent", agent_id="qa_agent", role="QA")
        builder.add_agent("docs", "Doc Agent", agent_id="doc_agent", role="TechnicalWriter")
        builder.add_end()

        builder.connect("START", "coder")
        builder.connect("coder", "qa")
        builder.connect("qa", "docs")
        builder.connect("docs", "END")
        return builder.build()

    @staticmethod
    def build_compliance_workflow() -> WorkflowGraph:
        builder = DAGBuilder("tmpl_compliance")
        builder.add_start()
        builder.add_agent("auditor", "Compliance Auditor", agent_id="auditor_agent", role="Auditor")
        builder.add_approval("signoff", "Compliance Signoff", approver_role="compliance_officer")
        builder.add_end()

        builder.connect("START", "auditor")
        builder.connect("auditor", "signoff")
        builder.connect("signoff", "END")
        return builder.build()

    @staticmethod
    def build_approval_workflow() -> WorkflowGraph:
        builder = DAGBuilder("tmpl_generic_approval")
        builder.add_start()
        builder.add_approval("human_check", "Governance Approval", approver_role="manager")
        builder.add_end()

        builder.connect("START", "human_check")
        builder.connect("human_check", "END")
        return builder.build()

    @staticmethod
    def build_incident_response_workflow() -> WorkflowGraph:
        builder = DAGBuilder("tmpl_incident_response")
        builder.add_start()
        builder.add_tool("alert", "Send Slack Alert", tool_name="slack_tool")
        builder.add_agent("investigator", "Security Agent", agent_id="security_agent", role="SecOps")
        builder.add_approval("mitigate", "Approve Mitigation", approver_role="soc_lead")
        builder.add_end()

        builder.connect("START", "alert")
        builder.connect("alert", "investigator")
        builder.connect("investigator", "mitigate")
        builder.connect("mitigate", "END")
        return builder.build()

    @staticmethod
    def build_knowledge_ingestion_workflow() -> WorkflowGraph:
        builder = DAGBuilder("tmpl_knowledge_ingestion")
        builder.add_start()
        builder.add_tool("extractor", "Extract Text", tool_name="text_extractor")
        builder.add_knowledge("indexer", "Index Documents", action="retrieve")
        builder.add_end()

        builder.connect("START", "extractor")
        builder.connect("extractor", "indexer")
        builder.connect("indexer", "END")
        return builder.build()
