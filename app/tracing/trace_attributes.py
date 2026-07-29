class TraceAttributes:
    # OpenTelemetry Standard Semantic Conventions
    HTTP_METHOD = "http.method"
    HTTP_STATUS_CODE = "http.status_code"
    HTTP_URL = "http.url"
    HTTP_TARGET = "http.target"
    HTTP_USER_AGENT = "user_agent.original"
    NET_PEER_IP = "net.peer.ip"
    SERVICE_NAME = "service.name"
    SERVICE_VERSION = "service.version"
    ENVIRONMENT = "deployment.environment"

    # LLM Gateway Custom Semantic Conventions
    LLM_PROVIDER = "llm.provider"
    LLM_MODEL = "llm.model"
    LLM_PROMPT_TOKENS = "llm.usage.prompt_tokens"
    LLM_COMPLETION_TOKENS = "llm.usage.completion_tokens"
    LLM_TOTAL_TOKENS = "llm.usage.total_tokens"
    LLM_COST = "llm.cost"
    LLM_LATENCY_MS = "llm.latency_ms"
    LLM_STREAMING = "llm.streaming"
    LLM_ROUTING_POLICY = "llm.routing.policy"
    LLM_RETRY_COUNT = "llm.retry_count"

    # Organization & User Context
    REQUEST_ID = "request.id"
    ORG_ID = "organization.id"
    WORKSPACE_ID = "workspace.id"
    USER_ID = "user.id"

    # Plugin Context
    PLUGIN_ID = "plugin.id"
    PLUGIN_NAME = "plugin.name"
    PLUGIN_HOOK = "plugin.hook"
    PLUGIN_STATUS = "plugin.status"

    # Component & Error Flags
    COMPONENT = "component"
    ERROR = "error"
    ERROR_TYPE = "error.type"
    ERROR_MESSAGE = "error.message"
