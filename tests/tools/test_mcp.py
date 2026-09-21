"""
Tests for Model Context Protocol (MCP) Subsystem
"""

import pytest

from app.tools.mcp.client import MCPClient
from app.tools.mcp.registry import MCPRegistry
from app.tools.mcp.server import MCPServer
from app.tools.mcp.transport import InMemoryTransport


@pytest.mark.asyncio
async def test_mcp_server_client_in_memory_flow():
    server = MCPServer(name="test-mcp-server")

    # Register a tool on the server
    def calculate_add(a: int, b: int) -> int:
        return a + b

    server.register_tool("add_tool", "Adds two numbers", calculate_add)
    server.register_resource("file:///docs/readme.txt", "Readme Documentation")
    server.register_prompt("summarize", "Summarizes text")

    # Connect client via InMemoryTransport
    transport = InMemoryTransport(server)
    client = MCPClient(transport=transport)
    await client.connect()

    # 1. Discover tools
    tools = await client.discover_tools()
    assert len(tools) == 1
    assert tools[0].name == "add_tool"

    # 2. Execute tool
    exec_res = await client.execute_tool("add_tool", {"a": 10, "b": 25})
    assert "35" in str(exec_res)

    # 3. List resources & prompts
    resources = await client.list_resources()
    assert len(resources) == 1
    assert resources[0].uri == "file:///docs/readme.txt"

    prompts = await client.get_prompts()
    assert len(prompts) == 1
    assert prompts[0].name == "summarize"

    # 4. Health check
    is_healthy = await client.health_check()
    assert is_healthy is True

    await client.close()


@pytest.mark.asyncio
async def test_mcp_registry():
    registry = MCPRegistry()
    server = MCPServer(name="reg-server")
    registry.register_server("srv_1", server)

    capabilities = await registry.discover_capabilities()
    assert "srv_1" in capabilities
    assert len(capabilities["srv_1"]["tools"]) == 0

    health = await registry.health_monitoring()
    assert health["srv_1"]["status"] == "healthy"

    removed = registry.remove_server("srv_1")
    assert removed is True
