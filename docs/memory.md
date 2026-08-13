# Enterprise Memory Platform (Phase 5.3)

## Architecture Overview

The Enterprise Memory Platform provides multi-tenant long-term contextual intelligence across Agents (Phase 5.1), Workflows (Phase 5.2), Knowledge (Phase 5.0), and the AI Gateway (Phase 4.7).

```text
                                  User Prompt / API Request
                                              │
                                              ▼
                                   Memory Extraction Engine
                                              │
                                              ▼
                                 Memory Classification Engine
                                              │
                                ┌─────────────┴─────────────┐
                                ▼                           ▼
                      Classification Result        Importance & Retention
                                │                           │
                                └─────────────┬─────────────┘
                                              ▼
                                  Unified Memory Store & Vector DB
                                              │
                                              ▼
                                 Multi-Strategy Memory Retriever
                                              │
                                              ▼
                                   Composite Memory Ranker
                                              │
                                              ▼
                                   Memory Context Assembler
                                              │
                                              ▼
                                    Agent / Workflow Prompt
```

---

## Core Memory Tiers

1. **Working Memory**: In-memory, per-execution scratchpad for planner state, reflection, reasoning traces, and tool outputs.
2. **Conversation Memory**: Multi-turn message history buffer with sliding window trimming, token budgeting, and summary compression.
3. **Semantic Memory**: Learned facts, user preferences, technology choices, and domain knowledge indexed via vector embeddings and hybrid search.
4. **Profile Memory**: User profile attributes, communication styles, technical preferences, coding patterns, and personalization settings.
5. **Session Memory**: Active project, workflow, and task context with automatic expiration, snapshots, and recovery.
6. **Episodic Memory**: Historical execution episodes (Agent runs, Workflow runs, Tool runs) enabling recall over past experiences.

---

## Ranking Formula

Candiate memory records are scored and sorted using composite weighted ranking:

$$\text{FinalScore} = (w_{\text{sim}} \cdot S_{\text{sim}}) + (w_{\text{rec}} \cdot S_{\text{rec}}) + (w_{\text{imp}} \cdot S_{\text{imp}}) + (w_{\text{conf}} \cdot S_{\text{conf}})$$

Default weights:
- Similarity Weight ($w_{\text{sim}}$): `0.4`
- Recency Weight ($w_{\text{rec}}$): `0.2`
- Importance Weight ($w_{\text{imp}}$): `0.2`
- Confidence Weight ($w_{\text{conf}}$): `0.2`

---

## REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/v1/memory` | Create a new memory record |
| `GET` | `/v1/memory` | List memory records for tenant |
| `GET` | `/v1/memory/{id}` | Get memory record details |
| `DELETE` | `/v1/memory/{id}` | Delete memory record |
| `POST` | `/v1/memory/search` | Execute multi-strategy vector & keyword search |
| `POST` | `/v1/memory/compress` | Compress conversation memory history |
| `POST` | `/v1/memory/summarize` | Summarize text content |
| `POST` | `/v1/memory/archive` | Archive memory record |
| `GET` | `/v1/memory/profile` | Retrieve user profile memory |
| `PATCH` | `/v1/memory/profile` | Update user profile memory |
| `GET` | `/v1/memory/analytics` | Fetch memory platform usage analytics |

---

## Python SDK Example

```python
from sdk.python.llm_engine import LLMEngineClient

client = LLMEngineClient(base_url="http://localhost:8000")

# Create memory record
entry = client.memory.create(
    content="User prefers Python FastAPI over Flask",
    context_hint="profile",
    user_id="user_123"
)

# Search memory
results = client.memory.search("What framework does user prefer?")

# Update user profile
client.memory.update_profile(
    user_id="user_123",
    profile_data={"preferred_framework": "fastapi"}
)
```

---

## CLI Commands

```bash
# Create memory
llm-engine memory create "Team uses PostgreSQL for persistent storage"

# Search memory
llm-engine memory search "database"

# Get profile
llm-engine memory profile --user-id user_123

# Memory analytics
llm-engine memory analytics
```
