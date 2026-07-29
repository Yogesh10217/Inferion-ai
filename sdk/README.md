# Official Client SDKs

Welcome to the official client SDKs for the LLM Inference Engine.

These SDKs provide an idiomatic, typed interface across multiple languages to interface with the AI Gateway.

## Supported Languages
- [Python](./python/)
- [TypeScript](./typescript/)
- [Go](./go/)
- [Java](./java/)

## Core Capabilities
- **Authentication**: Native support for API Keys and JWT.
- **Inference**: Chat, Completion, and Multi-modal APIs.
- **Streaming**: Native streaming paradigms (`async for`, `AsyncIterable`, Channels, Reactive Streams).
- **Administration**: Manage Organizations, Workspaces, Billing, Webhooks, and Plugins directly from code.

## Generating the Base
The core clients are generated from our unified `sdk/shared/openapi.json`. We manually wrap these generated clients with thin, idiomatic layers.
