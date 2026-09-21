"""Unit tests for Custom Agents, Workflow Templates, and MCP Packages."""

from app.extensions.agent_extension import AgentCapabilityManifest, AgentExtensionAdapter, AgentTemplate
from app.extensions.mcp_package import MCPPackage, MCPPackageManager, MCPServerManifest
from app.extensions.workflow_template import WorkflowTemplate, WorkflowTemplateEngine


def test_agent_workflow_mcp_extensions():
    # 1. Custom Agent Template
    agent_adapter = AgentExtensionAdapter()
    tmpl = AgentTemplate(
        template_id="custom_agent_1",
        name="Custom Data Agent",
        capability_manifest=AgentCapabilityManifest(agent_type="data_analyst", default_tools=["tool_csv"]),
    )
    agent = agent_adapter.register_custom_agent_template(tmpl, tenant_id="tenant_ext")
    assert agent.config.name == "Custom Data Agent"

    # 2. Workflow Template
    wf_engine = WorkflowTemplateEngine()
    wf_tmpl = WorkflowTemplate(
        template_id="research_auto",
        name="Research Automation",
        category="Research Automation",
        nodes_config=[{"id": "n1", "type": "AGENT"}],
        edges_config=[{"source": "START", "target": "n1"}, {"source": "n1", "target": "END"}],
    )
    graph = wf_engine.instantiate_template(wf_tmpl, tenant_id="tenant_ext")
    assert "n1" in graph.nodes

    # 3. MCP Package
    mcp_mgr = MCPPackageManager()
    mcp_pkg = MCPPackage(
        package_id="mcp_fs",
        manifest=MCPServerManifest(
            package_name="filesystem-mcp", command="npx", args=["-y", "@modelcontextprotocol/server-filesystem"]
        ),
        tenant_id="tenant_ext",
    )
    mcp_server = mcp_mgr.register_mcp_package(mcp_pkg)
    assert mcp_server.server_info.name == "filesystem-mcp"
