class TraceAttributes:
    # OpenTelemetry Semantics
    HTTP_METHOD = "http.method"
    HTTP_STATUS_CODE = "http.status_code"
    
    # LLM Inference Engine Semantics
    LLM_PROVIDER = "llm.provider"
    LLM_MODEL = "llm.model"
    LLM_PROMPT_TOKENS = "llm.usage.prompt_tokens"
    LLM_COMPLETION_TOKENS = "llm.usage.completion_tokens"
    LLM_COST = "llm.cost"
    ORG_ID = "organization.id"
    WORKSPACE_ID = "workspace.id"
