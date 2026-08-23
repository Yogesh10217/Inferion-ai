from .knowledge import KnowledgeClient, AsyncKnowledgeClient
from .agents import AgentsClient
from .workflows import WorkflowClient
from .memory import MemoryClient
from .tools import ToolsClient
from .teams import TeamsClient
from .planning import PlanningClient
from .autonomy import AutonomyClient, WorkersClient
from .observability import ObservabilityClient
from .reliability import SecurityClient, GovernanceClient, JobsClient, ReliabilityClient
from .control_plane import ControlPlaneClient
from .developers import DevelopersClient
from .extensions import ExtensionsClient
from .marketplace import MarketplaceClient
from .data_fabric import DataFabricClient
from .mlops import MLOpsClient
from .finops import FinOpsClient
from .operations import OperationsClient
from .governance import GovernanceClient as GovernancePlatformClient
from .identity import IdentityClient
from .orchestration import OrchestrationClient
from .knowledge_platform import KnowledgePlatformClient
from .integrations import IntegrationClient
from .developer_platform import DeveloperPlatformClient
from .applications import ApplicationPlatformClient
from .platform_operations import PlatformOperationsClient
from .intelligence import IntelligenceClient
from .data_governance import DataGovernanceClient
















import httpx

from typing import List, Dict, Any, Optional, AsyncGenerator
from .auth import AuthProvider, APIKeyAuth, BearerAuth
from .exceptions import APIError, AuthenticationError, RateLimitError, TimeoutError
from .models import ChatCompletionRequest, ChatCompletionResponse, ModelInfo
from .streaming import stream_sse_responses

class LLMEngineClient:
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        auth_provider: Optional[AuthProvider] = None,
        organization_id: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        
        headers = {"Content-Type": "application/json"}
        if organization_id:
            headers["X-Organization-ID"] = organization_id
            
        if auth_provider:
            headers.update(auth_provider.get_headers())
        elif api_key:
            headers.update(APIKeyAuth(api_key).get_headers())

        self.client = httpx.Client(base_url=self.base_url, headers=headers, timeout=self.timeout)
        self.knowledge = KnowledgeClient(self.client)
        self.agents = AgentsClient(self.client, self.base_url)
        self.workflows = WorkflowClient(self.client, self.base_url)
        self.memory = MemoryClient(self.client, self.base_url)
        self.tools = ToolsClient(self.base_url, api_key)
        self.teams = TeamsClient(self.base_url, api_key)
        self.planning = PlanningClient(self.base_url, api_key)
        self.autonomy = AutonomyClient(self.base_url, api_key)
        self.workers = WorkersClient(self.base_url, api_key)
        self.observability = ObservabilityClient(self.client, self.base_url)
        self.control_plane = ControlPlaneClient(self.base_url, api_key)
        self.developers = DevelopersClient(self.base_url, api_key)
        self.extensions = ExtensionsClient(self.base_url, api_key)
        self.marketplace = MarketplaceClient(self.base_url, api_key)
        self.data_fabric = DataFabricClient(self.base_url, api_key)
        self.finops = FinOpsClient(self.base_url, api_key)
        self.operations = OperationsClient(self.base_url, api_key)
        self.governance_platform = GovernancePlatformClient(self.base_url, api_key)
        self.identity_platform = IdentityClient(self.base_url, api_key)
        self.orchestration = OrchestrationClient(self.base_url, api_key)
        self.knowledge_platform = KnowledgePlatformClient(self.base_url, api_key)
        self.integrations = IntegrationClient(self.base_url, api_key)
        self.developer_platform = DeveloperPlatformClient(self.base_url, api_key)
        self.applications = ApplicationPlatformClient(self.base_url, api_key)
        self.platform_operations = PlatformOperationsClient(self.client)
        self.intelligence = IntelligenceClient(self.client)
        self.data_governance = DataGovernanceClient(self.client)



















    def health(self) -> dict:
        res = self.client.get("/health")
        return res.json()

    def list_models(self) -> List[ModelInfo]:
        res = self.client.get("/v1/models")
        data = res.json()
        models_raw = data.get("data", []) if isinstance(data, dict) else data
        return [ModelInfo(**m) for m in models_raw]

    def create_chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        res = self.client.post("/v1/chat/completions", json=request.model_dump())
        if res.status_code == 401:
            raise AuthenticationError("Invalid API key or credentials")
        elif res.status_code == 429:
            raise RateLimitError("Rate limit exceeded")
        elif res.status_code >= 400:
            raise APIError(f"API request failed with status {res.status_code}", status_code=res.status_code)
        return ChatCompletionResponse(**res.json())

class AsyncLLMEngineClient:
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        auth_provider: Optional[AuthProvider] = None,
        organization_id: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        
        headers = {"Content-Type": "application/json"}
        if organization_id:
            headers["X-Organization-ID"] = organization_id
            
        if auth_provider:
            headers.update(auth_provider.get_headers())
        elif api_key:
            headers.update(APIKeyAuth(api_key).get_headers())

        self.client = httpx.AsyncClient(base_url=self.base_url, headers=headers, timeout=self.timeout)
        self.knowledge = AsyncKnowledgeClient(self.client)

    async def health(self) -> dict:
        res = await self.client.get("/health")
        return res.json()

    async def create_chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        res = await self.client.post("/v1/chat/completions", json=request.model_dump())
        if res.status_code == 401:
            raise AuthenticationError("Invalid API key or credentials")
        elif res.status_code == 429:
            raise RateLimitError("Rate limit exceeded")
        elif res.status_code >= 400:
            raise APIError(f"API request failed with status {res.status_code}", status_code=res.status_code)
        return ChatCompletionResponse(**res.json())

    async def stream_chat_completion(self, request: ChatCompletionRequest) -> AsyncGenerator[dict, None]:
        req_data = request.model_dump()
        req_data["stream"] = True
        async with self.client.stream("POST", "/v1/chat/completions", json=req_data) as response:
            async for chunk in stream_sse_responses(response):
                yield chunk

    async def close(self):
        await self.client.aclose()
