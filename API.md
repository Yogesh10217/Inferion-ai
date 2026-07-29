# API Reference

## Health

### GET /v1/health

Returns a simple health payload.

Example response:

```json
{"status": "ok"}
```

### GET /v1/ready

Returns readiness status.

### GET /v1/live

Returns liveness status.

## Models

### GET /v1/models

Returns an OpenAI-compatible model list.

Example response:

```json
{
  "object": "list",
  "data": [
    {
      "id": "gpt-4o-mini",
      "object": "model",
      "created": 0,
      "owned_by": "openai"
    }
  ]
}
```

## Chat Completions

### POST /v1/chat/completions

Creates a chat completion.

Request body:

```json
{
  "model": "gpt-4o-mini",
  "messages": [{"role": "user", "content": "Hello"}],
  "stream": false
}
```

Response:

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
        "content": "Hello"
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

## Streaming

Set `stream: true` to receive a Server-Sent Events stream with `text/event-stream`.

## Plugin Admin API

- GET /v1/plugins: List plugins
- GET /v1/plugins/{id}: Get plugin details
- POST /v1/plugins/install: Install plugin
- PATCH /v1/plugins/{id}/enable: Enable plugin
- PATCH /v1/plugins/{id}/disable: Disable plugin
- DELETE /v1/plugins/{id}: Uninstall plugin
- POST /v1/plugins/{id}/reload: Reload plugin
- POST /v1/plugins/{id}/restart: Restart plugin
- GET /v1/plugins/{id}/health: Check plugin health
