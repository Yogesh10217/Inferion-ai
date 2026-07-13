# API Documentation

This document describes the API endpoints, request schemas, response formats, and error response standards.

## Endpoint Overview

All API endpoints are grouped under the default prefix `/v1`.

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| GET | `/v1/health` | Service health status | None |
| GET | `/v1/ready` | Service readiness status | None |
| GET | `/v1/live` | Service liveness status | None |
| GET | `/v1/models` | List available models | None |
| POST | `/v1/chat/completions` | Create chat completions (streaming or non-streaming) | None (mock key check) |

---

## 1. Chat Completion API

Creates assistant responses for a sequence of chat messages. Compatible with OpenAI API contracts.

### Request Specification
- **URL**: `/v1/chat/completions`
- **Method**: `POST`
- **Headers**:
  - `Content-Type: application/json`
  - `X-Request-ID: <string>` (Optional, custom correlation ID)
- **JSON Payload Fields**:
  - `model` (string, required): Model identifier (e.g., `gpt-4o-mini`, `llama3.1`).
  - `messages` (array of objects, required): Chat dialogue list. Each message contains:
    - `role` (string): `user`, `assistant`, or `system`.
    - `content` (string): The text content of the message.
  - `temperature` (float, optional, default: `0.7`): Sampling temperature between `0.0` and `2.0`.
  - `max_tokens` (integer, optional): Upper bound of output tokens.
  - `stream` (boolean, optional, default: `false`): Stream token chunks as Server-Sent Events (SSE).

### Response Specification (Non-Streaming)
- **Status**: `200 OK`
- **JSON Structure**:
```json
{
  "id": "chatcmpl-placeholder",
  "object": "chat.completion",
  "created": 0,
  "model": "gpt-4o-mini",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "[openai:gpt-4o-mini] Hello, how can I help you?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  }
}
```

### Response Specification (Streaming)
- **Status**: `200 OK`
- **Headers**: `Content-Type: text/event-stream`
- **Payload Format**: A sequence of Server-Sent Events ending with `data: [DONE]`.
```
data: {"id": "chatcmpl-gpt-4o-mini", "object": "chat.completion.chunk", "created": 1720892040, "model": "gpt-4o-mini", "choices": [{"index": 0, "delta": {"content": "[openai:gpt-4o-mini]"}, "finish_reason": null}]}

data: {"id": "chatcmpl-gpt-4o-mini", "object": "chat.completion.chunk", "created": 1720892040, "model": "gpt-4o-mini", "choices": [{"index": 0, "delta": {"content": " Hello,"}, "finish_reason": null}]}

...

data: [DONE]
```

---

## 2. Models API

Lists the models currently active in the service registry.

- **URL**: `/v1/models`
- **Method**: `GET`
- **Response Structure**:
```json
{
  "object": "list",
  "data": [
    {
      "id": "gpt-4o-mini",
      "object": "model",
      "created": 0,
      "owned_by": "openai"
    },
    {
      "id": "llama3.1",
      "object": "model",
      "created": 0,
      "owned_by": "ollama"
    }
  ]
}
```

---

## 3. Health & Observability APIs

Aggregated system state reporting compiled by `HealthService`.

- **URL**: `/v1/health` (or `/v1/ready`, `/v1/live`)
- **Method**: `GET`
- **Response Structure**:
```json
{
  "status": "ok",
  "overall_status": "healthy",
  "application_version": "0.1.0",
  "uptime": 12.345,
  "startup_timestamp": "2026-07-13T14:40:58.185044+00:00",
  "registered_providers": ["openai", "ollama"],
  "registered_models": ["gpt-4o-mini", "llama3.1"],
  "provider_health": {
    "openai": "healthy",
    "ollama": "healthy"
  },
  "application_state": "healthy",
  "request_count": 5,
  "memory_usage": "0 MB"
}
```

---

## Centralized Exception & Error Format

Errors are mapped to appropriate HTTP status codes and returned as a consistent JSON payload. Stack traces are never exposed to clients.

### JSON Error Schema
```json
{
  "error": {
    "code": "error_code_string",
    "message": "Human-readable description of what went wrong",
    "details": {}
  }
}
```

### Standard Status Codes Mapping
- **400 Bad Request** (`validation_error`): Invalid request payload (e.g., negative temperature, empty messages).
- **404 Not Found** (`model_not_found`): The requested model ID does not exist in the registry.
- **422 Unprocessable Entity** (`validation_error`): Pydantic payload parsing failures. Includes field-level validation errors in the `details` field.
- **500 Internal Server Error** (`internal_error` / `routing_failed` / `configuration_error`): Unexpected errors, config anomalies, or router strategy execution errors.
- **502 Bad Gateway** (`provider_unavailable`): Downstream LLM provider is down or timed out.
