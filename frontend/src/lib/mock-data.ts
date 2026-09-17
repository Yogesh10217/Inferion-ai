// ─────────────────────────────────────────────────────────────────────────────
// Inferion AI — Dashboard Mock Data
// Shaped after real backend API responses. Swap API_BASE_URL to go live.
// ─────────────────────────────────────────────────────────────────────────────

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8002";

// ── Overview ──────────────────────────────────────────────────────────────────
export const overviewStats = {
  totalRequests: 1_284_392,
  costToday: 47.83,
  activeAgents: 14,
  p99LatencyMs: 18.4,
  successRate: 99.7,
  tokensToday: 82_400_000,
};

export const requestTimeSeries = [
  { date: "Sep 10", requests: 142300, cost: 38.1 },
  { date: "Sep 11", requests: 168200, cost: 43.9 },
  { date: "Sep 12", requests: 155800, cost: 41.2 },
  { date: "Sep 13", requests: 194500, cost: 52.3 },
  { date: "Sep 14", requests: 211000, cost: 57.0 },
  { date: "Sep 15", requests: 198700, cost: 53.4 },
  { date: "Sep 16", requests: 213892, cost: 47.8 },
];

export const providerVolume = [
  { provider: "OpenAI GPT-4o", requests: 512000, color: "#0a152d" },
  { provider: "Ollama Llama3", requests: 384000, color: "#3b82f6" },
  { provider: "OpenAI GPT-4o-mini", requests: 261000, color: "#6366f1" },
  { provider: "Anthropic Claude", requests: 127392, color: "#8b5cf6" },
];

export const systemHealth = [
  { name: "FastAPI Gateway", status: "healthy", latency: "2ms" },
  { name: "Redis Cache", status: "healthy", latency: "0.4ms" },
  { name: "PostgreSQL DB", status: "healthy", latency: "3ms" },
  { name: "Ollama (Local)", status: "healthy", latency: "11ms" },
  { name: "OpenAI API", status: "healthy", latency: "142ms" },
  { name: "Prometheus", status: "healthy", latency: "1ms" },
];

export const recentRoutingDecisions = [
  {
    id: "rtd-001",
    timestamp: "2026-09-16T07:28:11Z",
    org: "Engineering",
    workspace: "backend-team",
    model: "gpt-4o",
    selectedProvider: "OpenAI",
    latencyMs: 14,
    costUsd: 0.0032,
    stage: "Selection",
    reason: "Capability match + lowest latency score",
  },
  {
    id: "rtd-002",
    timestamp: "2026-09-16T07:27:55Z",
    org: "Sales",
    workspace: "crm-bot",
    model: "llama3",
    selectedProvider: "Ollama",
    latencyMs: 9,
    costUsd: 0.0,
    stage: "Policy Override",
    reason: "Cost policy: prefer local for non-critical tasks",
  },
  {
    id: "rtd-003",
    timestamp: "2026-09-16T07:27:43Z",
    org: "Finance",
    workspace: "report-gen",
    model: "claude-3-5-sonnet",
    selectedProvider: "Anthropic",
    latencyMs: 22,
    costUsd: 0.0078,
    stage: "Failover",
    reason: "OpenAI circuit breaker triggered — failed over to Anthropic",
  },
  {
    id: "rtd-004",
    timestamp: "2026-09-16T07:27:30Z",
    org: "Engineering",
    workspace: "ci-assistant",
    model: "gpt-4o-mini",
    selectedProvider: "OpenAI",
    latencyMs: 8,
    costUsd: 0.0004,
    stage: "Selection",
    reason: "Cost-optimized: mini sufficient for classification task",
  },
  {
    id: "rtd-005",
    timestamp: "2026-09-16T07:27:18Z",
    org: "HR",
    workspace: "onboarding-bot",
    model: "llama3",
    selectedProvider: "Ollama",
    latencyMs: 11,
    costUsd: 0.0,
    stage: "Selection",
    reason: "Rule: sensitive PII data → local model required",
  },
];

// ── Routing ───────────────────────────────────────────────────────────────────
export const routingStages = [
  { stage: 1, name: "Capability Filter", desc: "Match model features (streaming, vision, function calling, context window)", icon: "🔍" },
  { stage: 2, name: "Rule Evaluation", desc: "Apply custom routing rules configured per tenant", icon: "📋" },
  { stage: 3, name: "Policy Evaluation", desc: "Compute cost optimization vs latency prioritization weights", icon: "⚖️" },
  { stage: 4, name: "Health Check", desc: "Circuit breaker validation for active model providers", icon: "🩺" },
  { stage: 5, name: "Weighted Scoring", desc: "Multi-criteria scoring based on real-time provider metrics", icon: "🧮" },
  { stage: 6, name: "Provider Ranking", desc: "Rank healthy candidates by composite score", icon: "📊" },
  { stage: 7, name: "Selection", desc: "Select optimal candidate provider", icon: "✅" },
  { stage: 8, name: "Failover", desc: "Fallback strategies on upstream provider errors", icon: "🔄" },
  { stage: 9, name: "Decision Trace", desc: "Explainable trace log stored for audit and analytics", icon: "📝" },
];

export const providerHealth = [
  { name: "OpenAI GPT-4o", status: "healthy", score: 97, latency: 142, errorRate: 0.1, circuitBreaker: "closed" },
  { name: "OpenAI GPT-4o-mini", status: "healthy", score: 99, latency: 84, errorRate: 0.0, circuitBreaker: "closed" },
  { name: "Ollama Llama3 (Local)", status: "healthy", score: 94, latency: 11, errorRate: 0.3, circuitBreaker: "closed" },
  { name: "Anthropic Claude 3.5", status: "degraded", score: 61, latency: 890, errorRate: 4.2, circuitBreaker: "half-open" },
  { name: "Azure OpenAI", status: "offline", score: 0, latency: 0, errorRate: 100, circuitBreaker: "open" },
];

// ── Agents ────────────────────────────────────────────────────────────────────
export const agents = [
  {
    id: "agt-dev-assistant",
    name: "Dev Assistant",
    strategy: "ReAct",
    status: "idle",
    tools: ["python", "shell", "knowledge_search"],
    lastRun: "2026-09-16T06:48:00Z",
    totalRuns: 412,
    avgLatencyMs: 3200,
    budgetUsed: 1.24,
    budgetMax: 2.0,
  },
  {
    id: "agt-report-gen",
    name: "Report Generator",
    strategy: "PlanExecute",
    status: "running",
    tools: ["rest_api", "knowledge_search", "calculator"],
    lastRun: "2026-09-16T07:22:00Z",
    totalRuns: 87,
    avgLatencyMs: 8700,
    budgetUsed: 3.88,
    budgetMax: 5.0,
  },
  {
    id: "agt-code-reviewer",
    name: "Code Reviewer",
    strategy: "TreeOfThought",
    status: "idle",
    tools: ["python", "shell"],
    lastRun: "2026-09-16T05:11:00Z",
    totalRuns: 234,
    avgLatencyMs: 5100,
    budgetUsed: 0.78,
    budgetMax: 3.0,
  },
  {
    id: "agt-crm-bot",
    name: "CRM Bot",
    strategy: "ZeroShot",
    status: "idle",
    tools: ["rest_api"],
    lastRun: "2026-09-16T07:25:00Z",
    totalRuns: 1820,
    avgLatencyMs: 410,
    budgetUsed: 0.12,
    budgetMax: 1.0,
  },
  {
    id: "agt-data-analyst",
    name: "Data Analyst",
    strategy: "PlanExecute",
    status: "error",
    tools: ["python", "calculator", "rest_api"],
    lastRun: "2026-09-16T04:30:00Z",
    totalRuns: 56,
    avgLatencyMs: 12400,
    budgetUsed: 4.99,
    budgetMax: 5.0,
  },
  {
    id: "agt-onboard-bot",
    name: "Onboarding Bot",
    strategy: "ReAct",
    status: "idle",
    tools: ["knowledge_search", "rest_api"],
    lastRun: "2026-09-16T07:28:00Z",
    totalRuns: 618,
    avgLatencyMs: 920,
    budgetUsed: 0.44,
    budgetMax: 2.0,
  },
];

export const agentRunLog = [
  { step: 1, type: "thought", content: "I need to find all failing tests first using pytest.", timestamp: "07:22:01" },
  { step: 2, type: "tool_call", tool: "shell", input: "pytest --tb=short 2>&1 | head -60", timestamp: "07:22:02" },
  { step: 3, type: "tool_result", content: "FAILED tests/test_routing.py::test_failover_trigger\nFAILED tests/test_agents.py::test_react_planner", timestamp: "07:22:04" },
  { step: 4, type: "thought", content: "Two failures. Let me read the test files to understand the root cause.", timestamp: "07:22:05" },
  { step: 5, type: "tool_call", tool: "python", input: "open('tests/test_routing.py').read()", timestamp: "07:22:06" },
  { step: 6, type: "thought", content: "The failover test expects a 503 response but the mock returns 500. I'll patch the mock.", timestamp: "07:22:09" },
  { step: 7, type: "tool_call", tool: "shell", input: "sed -i 's/status_code=500/status_code=503/' tests/test_routing.py", timestamp: "07:22:10" },
  { step: 8, type: "tool_call", tool: "shell", input: "pytest tests/test_routing.py -v", timestamp: "07:22:11" },
  { step: 9, type: "tool_result", content: "PASSED tests/test_routing.py::test_failover_trigger ✅", timestamp: "07:22:14" },
  { step: 10, type: "observation", content: "First test fixed. Moving to test_react_planner.", timestamp: "07:22:15" },
];

// ── API Keys ──────────────────────────────────────────────────────────────────
export const apiKeys = [
  {
    id: "key-001",
    key: "sk_live_eng_a7f3k2m9",
    name: "Engineering CI Pipeline",
    org: "Acme Corp",
    workspace: "Engineering",
    role: "developer",
    status: "active",
    lastUsed: "2026-09-16T07:28:11Z",
    quotaUsed: 42300,
    quotaMax: 50000,
    costMtd: 38.20,
  },
  {
    id: "key-002",
    key: "sk_live_sales_b2h7p1q5",
    name: "Sales CRM Integration",
    org: "Acme Corp",
    workspace: "Sales",
    role: "viewer",
    status: "active",
    lastUsed: "2026-09-16T07:25:30Z",
    quotaUsed: 8100,
    quotaMax: 10000,
    costMtd: 9.80,
  },
  {
    id: "key-003",
    key: "sk_live_fin_c9k4r3z8",
    name: "Finance Report Generator",
    org: "Acme Corp",
    workspace: "Finance",
    role: "developer",
    status: "active",
    lastUsed: "2026-09-16T06:50:00Z",
    quotaUsed: 3200,
    quotaMax: 5000,
    costMtd: 22.10,
  },
  {
    id: "key-004",
    key: "sk_live_hr_d1n8s5w2",
    name: "HR Onboarding Bot",
    org: "Acme Corp",
    workspace: "HR",
    role: "viewer",
    status: "active",
    lastUsed: "2026-09-16T07:20:00Z",
    quotaUsed: 1820,
    quotaMax: 3000,
    costMtd: 4.40,
  },
  {
    id: "key-005",
    key: "sk_live_old_e6q9t7y4",
    name: "Legacy Integration (deprecated)",
    org: "Acme Corp",
    workspace: "Engineering",
    role: "admin",
    status: "revoked",
    lastUsed: "2026-08-01T12:00:00Z",
    quotaUsed: 0,
    quotaMax: 50000,
    costMtd: 0,
  },
];

// ── Knowledge / RAG ───────────────────────────────────────────────────────────
export const knowledgeBases = [
  {
    id: "kb-001",
    name: "Engineering Runbooks",
    documents: 48,
    chunks: 2140,
    vectorStore: "FAISS",
    embeddingModel: "text-embedding-3-small",
    status: "indexed",
    lastUpdated: "2026-09-15T18:00:00Z",
    sizeKb: 3400,
  },
  {
    id: "kb-002",
    name: "Sales Playbook",
    documents: 22,
    chunks: 890,
    vectorStore: "Qdrant",
    embeddingModel: "text-embedding-3-small",
    status: "indexed",
    lastUpdated: "2026-09-14T10:30:00Z",
    sizeKb: 1200,
  },
  {
    id: "kb-003",
    name: "Finance Reports Q3",
    documents: 7,
    chunks: 312,
    vectorStore: "Pinecone",
    embeddingModel: "text-embedding-ada-002",
    status: "indexing",
    lastUpdated: "2026-09-16T07:00:00Z",
    sizeKb: 980,
  },
  {
    id: "kb-004",
    name: "Product Documentation",
    documents: 134,
    chunks: 6820,
    vectorStore: "Milvus",
    embeddingModel: "text-embedding-3-large",
    status: "indexed",
    lastUpdated: "2026-09-13T09:15:00Z",
    sizeKb: 18400,
  },
];

export const documentChunks = [
  { id: "chk-001", source: "runbook-deploy.md", text: "To deploy the inference engine, run `docker compose up -d --build`. The service exposes port 8002 by default and requires OPENAI_API_KEY to be set in the .env file.", score: 0.94 },
  { id: "chk-002", source: "runbook-rollback.md", text: "Rollback procedure: 1) Identify the previous stable image tag 2) Update docker-compose.yml 3) Run `docker compose up -d` — the health check will validate the rollback.", score: 0.88 },
  { id: "chk-003", source: "runbook-scaling.md", text: "Horizontal scaling is achieved via multiple replicas behind a load balancer. Redis must be shared across all instances for rate limiting and caching to function correctly.", score: 0.81 },
  { id: "chk-004", source: "runbook-monitoring.md", text: "Grafana dashboards are pre-provisioned at port 3000. Use the 'SLO Dashboard' to track error budgets and the 'Provider Routing' dashboard for traffic split visualization.", score: 0.76 },
  { id: "chk-005", source: "runbook-security.md", text: "All API keys are prefixed with `sk_live_` for production and `sk_test_` for staging. Keys are stored hashed (SHA-256) in PostgreSQL and are never returned after initial creation.", score: 0.71 },
];

// ── Memory ────────────────────────────────────────────────────────────────────
export const memoryEntries = {
  Working: [
    { id: "wm-001", userId: "usr-eng-01", content: "Current task: Fix CI pipeline — 2 failing tests identified", score: 1.0, ttl: "session", createdAt: "07:22:00" },
    { id: "wm-002", userId: "usr-eng-01", content: "Tool outputs buffer: pytest result = 2 failures in test_routing.py", score: 0.95, ttl: "session", createdAt: "07:22:04" },
  ],
  Conversation: [
    { id: "cm-001", userId: "usr-sales-01", content: "[User]: What's our Q3 deal pipeline? [AI]: Based on your CRM data, 14 active deals totaling $1.2M...", score: 0.88, ttl: "7d", createdAt: "2026-09-15" },
    { id: "cm-002", userId: "usr-eng-01", content: "[User]: Explain the routing engine. [AI]: The 9-stage pipeline starts with capability filter...", score: 0.84, ttl: "7d", createdAt: "2026-09-15" },
    { id: "cm-003", userId: "usr-fin-01", content: "[User]: Generate Q3 cost report. [AI]: Generating report for all workspaces...", score: 0.79, ttl: "7d", createdAt: "2026-09-14" },
  ],
  Semantic: [
    { id: "sm-001", userId: "usr-eng-01", content: "User prefers concise Python code with type hints", score: 0.91, ttl: "30d", createdAt: "2026-09-10" },
    { id: "sm-002", userId: "usr-eng-01", content: "Deployment environment uses Docker Compose on Ubuntu 22.04", score: 0.87, ttl: "30d", createdAt: "2026-09-08" },
    { id: "sm-003", userId: "usr-sales-01", content: "Prefers bullet-point summaries over long paragraphs", score: 0.83, ttl: "30d", createdAt: "2026-09-05" },
  ],
  Profile: [
    { id: "pm-001", userId: "usr-eng-01", content: "Role: Senior Backend Engineer | Stack: Python, FastAPI, Docker | Timezone: IST", score: 1.0, ttl: "permanent", createdAt: "2026-08-01" },
    { id: "pm-002", userId: "usr-sales-01", content: "Role: Sales Manager | Team: APAC | Tools: Salesforce, HubSpot", score: 1.0, ttl: "permanent", createdAt: "2026-08-01" },
  ],
  Session: [
    { id: "ss-001", userId: "usr-eng-01", content: "Active project: Inferion AI CI fix | Branch: fix/ci-failures | PR #42", score: 0.96, ttl: "24h", createdAt: "2026-09-16" },
    { id: "ss-002", userId: "usr-fin-01", content: "Active task: Q3 Finance Report generation — 60% complete", score: 0.91, ttl: "24h", createdAt: "2026-09-16" },
  ],
  Episodic: [
    { id: "ep-001", userId: "usr-eng-01", content: "Agent run agt-dev-assistant: Fixed 2 failing CI tests in 3.2s — SUCCESS", score: 0.78, ttl: "90d", createdAt: "2026-09-15" },
    { id: "ep-002", userId: "usr-eng-01", content: "Agent run agt-code-reviewer: Reviewed PR #39, found 4 issues — COMPLETED", score: 0.72, ttl: "90d", createdAt: "2026-09-14" },
    { id: "ep-003", userId: "usr-sales-01", content: "Report generated for weekly pipeline — 14 deals, $1.2M total — SUCCESS", score: 0.68, ttl: "90d", createdAt: "2026-09-13" },
  ],
};

// ── FinOps ────────────────────────────────────────────────────────────────────
export const workspaceBudgets = [
  { workspace: "Engineering", org: "Acme Corp", budgetMtd: 2000, usedMtd: 1284, requests: 512000 },
  { workspace: "Sales", org: "Acme Corp", budgetMtd: 500, usedMtd: 312, requests: 127000 },
  { workspace: "Finance", org: "Acme Corp", budgetMtd: 1000, usedMtd: 887, requests: 89000 },
  { workspace: "HR", org: "Acme Corp", budgetMtd: 300, usedMtd: 44, requests: 22000 },
  { workspace: "Product", org: "Acme Corp", budgetMtd: 800, usedMtd: 621, requests: 198000 },
];

export const costByModel = [
  { model: "GPT-4o", cost: 1820, tokens: 48200000 },
  { model: "GPT-4o-mini", cost: 412, tokens: 81400000 },
  { model: "Claude 3.5 Sonnet", cost: 710, tokens: 18900000 },
  { model: "Llama3 (Ollama)", cost: 0, tokens: 64100000 },
];

export const dailyCostTrend = [
  { day: "Sep 10", eng: 38, sales: 12, finance: 22, hr: 2 },
  { day: "Sep 11", eng: 44, sales: 14, finance: 28, hr: 2 },
  { day: "Sep 12", eng: 41, sales: 10, finance: 25, hr: 3 },
  { day: "Sep 13", eng: 52, sales: 18, finance: 31, hr: 2 },
  { day: "Sep 14", eng: 57, sales: 21, finance: 34, hr: 3 },
  { day: "Sep 15", eng: 53, sales: 16, finance: 29, hr: 2 },
  { day: "Sep 16", eng: 47, sales: 13, finance: 24, hr: 2 },
];

// ── Organizations ─────────────────────────────────────────────────────────────
export const organizations = [
  {
    id: "org-001",
    name: "Acme Corp",
    plan: "Enterprise",
    status: "active",
    workspaces: [
      { id: "ws-eng", name: "Engineering", users: 12, budgetMtd: 2000, quotaDay: 50000, usedDay: 42300 },
      { id: "ws-sales", name: "Sales", users: 8, budgetMtd: 500, quotaDay: 10000, usedDay: 8100 },
      { id: "ws-fin", name: "Finance", users: 4, budgetMtd: 1000, quotaDay: 5000, usedDay: 3200 },
      { id: "ws-hr", name: "HR", users: 3, budgetMtd: 300, quotaDay: 3000, usedDay: 1820 },
      { id: "ws-prod", name: "Product", users: 6, budgetMtd: 800, quotaDay: 20000, usedDay: 14200 },
    ],
  },
  {
    id: "org-002",
    name: "TechStart Inc",
    plan: "Growth",
    status: "active",
    workspaces: [
      { id: "ws-dev", name: "Development", users: 5, budgetMtd: 500, quotaDay: 10000, usedDay: 3200 },
      { id: "ws-mkt", name: "Marketing", users: 2, budgetMtd: 200, quotaDay: 3000, usedDay: 890 },
    ],
  },
  {
    id: "org-003",
    name: "AI Research Lab",
    plan: "Startup",
    status: "trial",
    workspaces: [
      { id: "ws-res", name: "Research", users: 3, budgetMtd: 100, quotaDay: 5000, usedDay: 2100 },
    ],
  },
];

// ── Plugins ───────────────────────────────────────────────────────────────────
export type PluginState = "active" | "installed" | "paused" | "error" | "loading" | "uninstalling" | "disabled";

export const plugins = [
  {
    id: "plg-001",
    name: "OpenTelemetry Exporter",
    description: "Exports distributed traces to Jaeger, Zipkin, or OTLP endpoint. Supports 5 exporter backends.",
    version: "2.1.0",
    author: "Inferion Core",
    state: "active" as PluginState,
    hooks: ["on_request_start", "on_response_end", "on_error"],
    category: "Observability",
  },
  {
    id: "plg-002",
    name: "PII Redaction Filter",
    description: "Automatically detects and redacts PII (names, emails, credit cards) before sending to external models.",
    version: "1.4.2",
    author: "Inferion Security",
    state: "active" as PluginState,
    hooks: ["on_request_transform", "on_response_transform"],
    category: "Security",
  },
  {
    id: "plg-003",
    name: "Semantic Cache",
    description: "Caches LLM responses using vector similarity — returns cached answers for semantically equivalent queries.",
    version: "1.2.0",
    author: "Community",
    state: "paused" as PluginState,
    hooks: ["on_request_start", "on_response_end"],
    category: "Performance",
  },
  {
    id: "plg-004",
    name: "Slack Webhook Notifier",
    description: "Sends webhook events (agent completions, budget alerts, errors) directly to configured Slack channels.",
    version: "1.0.5",
    author: "Community",
    state: "installed" as PluginState,
    hooks: ["on_event_published"],
    category: "Integrations",
  },
  {
    id: "plg-005",
    name: "Content Moderation",
    description: "Runs prompt and response through a moderation model. Blocks harmful content before it reaches the user.",
    version: "3.0.1",
    author: "Inferion Security",
    state: "active" as PluginState,
    hooks: ["on_request_validate", "on_response_validate"],
    category: "Security",
  },
  {
    id: "plg-006",
    name: "Cost Anomaly Detector",
    description: "ML-based anomaly detection on spending patterns. Fires alerts when cost deviates >2σ from the 30-day baseline.",
    version: "1.1.0",
    author: "Inferion FinOps",
    state: "error" as PluginState,
    hooks: ["on_request_end", "on_billing_event"],
    category: "FinOps",
  },
  {
    id: "plg-007",
    name: "SAML SSO Bridge",
    description: "Enables enterprise SAML 2.0 SSO authentication with Okta, Azure AD, and Google Workspace.",
    version: "2.0.0",
    author: "Inferion Identity",
    state: "disabled" as PluginState,
    hooks: ["on_auth_request"],
    category: "Identity",
  },
];
