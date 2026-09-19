"""
MCP Transports: InMemory, Stdio, and HTTP/SSE Transports
"""

import abc
import asyncio
import json
import logging
from typing import Optional

from app.tools.exceptions import MCPConnectionError
from app.tools.mcp.schemas import MCPJsonRpcRequest, MCPJsonRpcResponse

logger = logging.getLogger(__name__)


class MCPTransport(abc.ABC):
    """Abstract Transport Layer for MCP Client and Server communication."""

    @abc.abstractmethod
    async def connect(self) -> None:
        pass

    @abc.abstractmethod
    async def close(self) -> None:
        pass

    @abc.abstractmethod
    async def send_request(self, request: MCPJsonRpcRequest) -> MCPJsonRpcResponse:
        pass


class InMemoryTransport(MCPTransport):
    """In-memory transport directly connecting MCPClient to an MCPServer instance in process."""

    def __init__(self, server=None):
        self.server = server
        self._connected = False

    async def connect(self) -> None:
        self._connected = True

    async def close(self) -> None:
        self._connected = False

    async def send_request(self, request: MCPJsonRpcRequest) -> MCPJsonRpcResponse:
        if not self._connected or not self.server:
            raise MCPConnectionError("InMemoryTransport is not connected")
        return await self.server.handle_request(request)


class StdioTransport(MCPTransport):
    """Subprocess stdio transport communicating via standard I/O streams."""

    def __init__(self, command: str, args: Optional[list] = None):
        self.command = command
        self.args = args or []
        self.process = None
        self._connected = False

    async def connect(self) -> None:
        try:
            self.process = await asyncio.create_subprocess_exec(
                self.command,
                *self.args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            self._connected = True
            logger.info(f"Connected StdioTransport to '{self.command}'")
        except Exception as e:
            raise MCPConnectionError(f"Failed to launch stdio subprocess '{self.command}': {e}")

    async def close(self) -> None:
        if self.process:
            try:
                self.process.terminate()
                await self.process.wait()
            except Exception:  # nosec B110
                pass
        self._connected = False

    async def send_request(self, request: MCPJsonRpcRequest) -> MCPJsonRpcResponse:
        if not self._connected or not self.process:
            raise MCPConnectionError("StdioTransport is not connected")

        payload = json.dumps(request.model_dump()) + "\n"
        self.process.stdin.write(payload.encode("utf-8"))
        await self.process.stdin.drain()

        line = await self.process.stdout.readline()
        if not line:
            raise MCPConnectionError("Subprocess closed output stream unexpectedly")

        data = json.loads(line.decode("utf-8"))
        return MCPJsonRpcResponse(**data)


class HTTPTransport(MCPTransport):
    """HTTP/REST transport communicating with an external MCP HTTP endpoint."""

    def __init__(self, endpoint_url: str):
        self.endpoint_url = endpoint_url
        self._connected = False

    async def connect(self) -> None:
        self._connected = True

    async def close(self) -> None:
        self._connected = False

    async def send_request(self, request: MCPJsonRpcRequest) -> MCPJsonRpcResponse:
        if not self._connected:
            raise MCPConnectionError("HTTPTransport is not connected")

        import httpx

        async with httpx.AsyncClient() as client:
            resp = await client.post(self.endpoint_url, json=request.model_dump(), timeout=30.0)
            if resp.status_code != 200:
                raise MCPConnectionError(f"HTTP MCP request failed with status {resp.status_code}: {resp.text}")
            return MCPJsonRpcResponse(**resp.json())
