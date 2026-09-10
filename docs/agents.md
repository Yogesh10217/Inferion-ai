# Phase 5.1 – Enterprise Agent Framework Documentation

## Architecture Overview

The Enterprise Agent Framework provides a modular, production-grade autonomous agent execution engine built on top of the Inferion AI.

```
app/agents/
├── agent.py               # Core Agent driver
├── agent_manager.py       # Multi-tenant Agent orchestrator
├── agent_factory.py       # Template & Custom Agent Factory
├── agent_registry.py      # Agent definition repository
├── agent_config.py       # Agent configuration schemas
├── agent_session.py       # Session history manager
├── agent_state.py         # State machine & step models
├── agent_context.py       # Scoped tenant execution context
├── agent_events.py        # EventBus integration
├── checkpoint.py          # Session state snapshotting
├── approval.py            # Human-in-the-loop approval controller
├── budget.py              # Token & financial cost limit tracker
├── cache.py               # Planning & tool result caching engine
├── knowledge_adapter.py   # Phase 5.0 Knowledge & Citation bridge
├── exceptions.py         # Domain error hierarchy
│
├── planner/               # Multi-strategy planners (ZeroShot, ReAct, PlanExecute, ToT)
├── reflection/            # Self-Critique & LLM Judge reflection engines
├── memory/                # Working & Conversation memory coordinator
├── tools/                 # Dynamic tool registry & executor (Builtin, Python, Shell, REST, Plugin)
├── prompts/               # Versioned prompt templates
└── artifacts/             # Execution artifact manager & store
```

---

## Agent Lifecycle

```
User Request
     ↓
Context Assembly
     ↓
Knowledge Retrieval (Phase 5.0)
     ↓
Planning (ReAct / Plan-Execute / ToT)
     ↓
Tool Selection & Approval Check
     ↓
Tool Execution
     ↓
Observation Collection
     ↓
Reflection & Self-Critique
     ↓
Memory Update & Checkpoint
     ↓
Final Response
```

---

## API Endpoints (`/v1/agents`)

- `POST /v1/agents` - Create agent definition
- `GET /v1/agents` - List all agents
- `GET /v1/agents/{id}` - Get agent definition
- `DELETE /v1/agents/{id}` - Delete agent definition
- `POST /v1/agents/{id}/run` - Trigger autonomous execution
- `POST /v1/agents/sessions/{session_id}/resume` - Resume paused session / submit approval
- `POST /v1/agents/sessions/{session_id}/cancel` - Cancel active execution
- `GET /v1/agents/{id}/sessions` - List execution sessions for agent

---

## Python SDK Example

```python
from sdk.python.llm_engine.client import LLMEngineClient

client = LLMEngineClient(base_url="http://localhost:8002", api_key="sk_test")

# Create Agent
client.agents.create(
    agent_id="analyst_agent",
    name="Data Analyst Agent",
    description="Performs calculations and knowledge search",
    planner_strategy="react",
    tools=["calculator", "knowledge_search"]
)

# Run Agent
result = client.agents.run("analyst_agent", prompt="Calculate 25 * 4")
print(result)
```
