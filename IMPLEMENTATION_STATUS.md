# IMPLEMENTATION_STATUS.md — Current implementation & next actions

## What is implemented till now (Phase 1 foundation)

### 1) FastAPI gateway (transport layer)
- `app/main.py`
  - FastAPI app factory: `create_app()`.
  - Middleware:
    - CORS (`cors_origins` from env).
    - `LoggingMiddleware` (latency, status, request id, model/provider hints).
  - Routers wired under `API_PREFIX` (default `/v1`):
    - `/health`, `/ready`, `/live`
    - `/models`
    - `/chat/completions`

### 2) OpenAI-compatible routes
- `app/api/health.py`
  - `/v1/health`, `/v1/ready`, `/v1/live` return fixed statuses.
- `app/api/models.py`
  - `/v1/models` returns an OpenAI-like list response.
  - Uses in-memory registry (`InMemoryModelRegistry`).
- `app/api/chat.py`
  - `POST /v1/chat/completions`
    - If `stream=false`:
      - Calls `InferenceService.complete()` and wraps the provider text into an OpenAI-compatible response.
      - Note: the current response uses placeholder fields for `id/object/created` and sets `usage` to zeros.
    - If `stream=true`:
      - Creates a `StreamingResponse` with `text/event-stream`.
      - Streams output from `InferenceService.stream_completion()`.

### 3) Schemas (request/response contract)
- `app/schemas/request.py`
  - `ChatMessage`, `InferenceRequest` and `ChatCompletionRequest`.
  - Includes common sampling params validation (temperature/top_p/max_tokens/etc.).
- `app/schemas/response.py`
  - OpenAI-like response models: `ChatCompletionResponse`, `Choice`, `Usage`, plus models-list response.
- `app/schemas/inference_response.py`
  - Provider-normalized response: `InferenceResponse` + `Usage`.

### 4) Provider abstraction layer
- `app/providers/base_provider.py`
  - Defines provider interface:
    - `generate()`
    - `stream()`
    - `health_check()`
    - `list_models()`
- `app/providers/openai_provider.py`
  - **Currently a stub/mock implementation**.
  - `generate()` returns text in the form: `[openai:{model}] {prompt}`.
  - `stream()` yields OpenAI-style chunk strings but does **not** call real OpenAI APIs.
  - `health_check()` always returns `True`.
  - `list_models()` returns example model metadata (hardcoded).
- `app/providers/ollama_provider.py`
  - **Currently a stub/mock implementation**.
  - `generate()` returns text in the form: `[ollama:{model}] {prompt}`.
  - `stream()` yields chunk strings but does **not** call real Ollama APIs.
  - `health_check()` always returns `True`.
  - `list_models()` returns example model metadata (hardcoded).

### 5) Model registry
- `app/registry/model_registry.py`
  - `ModelRegistry` interface.
  - `InMemoryModelRegistry`:
    - Thread-safe via `RLock`.
    - Seeds two models:
      - `gpt-4o-mini` -> `openai`
      - `llama3.1` -> `ollama`

### 6) Inference service / orchestration
- `app/services/inference_service.py`
  - `DefaultInferenceService` implements:
    - `complete(model_id, prompt, **kwargs)`
      - Validates request: model exists + status `available`.
      - Resolves provider:
        - If `RequestRouter` exists, it calls `request_router.route(...)`.
        - Else uses a single configured provider instance.
      - Calls `provider.generate()`.
    - `stream_completion(model_id, prompt, **kwargs)`
      - Validates + resolves provider.
      - Wraps each token/stream chunk into SSE `data: {json}\n\n`.
      - Ends with `data: [DONE]\n\n`.

### 7) Exceptions / error handling
- `app/core/exceptions.py`
  - Standardized `AppException` with payload: `{ error: { code, message, details } }`.
  - `AppExceptionHandler.handle()` used by `LoggingMiddleware` and can be expanded to route-level handlers.

### 8) Tests
- `tests/test_health.py`
  - Validates `/v1/health`, `/v1/ready`, `/v1/live`.

## What is NOT implemented fully (gaps to complete Phase 1)

### A) Real backend integrations (highest priority)
- `OpenAIProvider` currently does not call OpenAI.
- `OllamaProvider` currently does not call the Ollama HTTP API.

### B) Provider health checks & model discovery
- `health_check()` always returns `True`.
- `/v1/models` is based only on the seeded in-memory registry.
- The registry should eventually be seeded/discovered from providers.

### C) Correct OpenAI-compatible payloads
Current `/v1/chat/completions` response has placeholder behavior:
- Non-stream response sets `id/object/created` as placeholders.
- `usage` is currently all zeros at the API layer.
- Streaming wrapper in `InferenceService.stream_completion()` assumes provider yields tokens, but the providers currently yield SSE-formatted lines (schema mismatch risk).

### D) Consistent error handling from service/provider
- `InferenceService` raises custom exceptions, but there is no route-level try/except in `chat.py`.
- Middleware handles `AppException`, but you should ensure all provider failures are wrapped as `AppException` types (and that status codes/messages are consistent).

### E) Request validation hardening
- `ChatCompletionRequest` currently just inherits `InferenceRequest`.
- Ensure `messages` shape and required params match OpenAI semantics (e.g., `model` presence, `stream` behavior, optional defaults).

### F) End-to-end smoke tests
- Tests exist for health only so far.
- Add E2E tests for:
  - `/v1/models`
  - `/v1/chat/completions` (stream and non-stream)
  - provider error paths

## Next actions checklist (what should be done)

### Provider integration tasks
- [ ] Implement real OpenAI SDK call in `OpenAIProvider.generate()` + streaming.
- [ ] Implement real Ollama HTTP calls in `OllamaProvider.generate()` + streaming.
- [ ] Wire provider configuration from `app/core/config.py` env:
  - `OPENAI_API_KEY`, `OLLAMA_BASE_URL`, etc.

### Model registry / discovery tasks
- [ ] Add startup seeding of registry from providers (using `provider.list_models()`).
- [ ] Ensure `/v1/models` returns real model metadata with provider attribution.

### Health checks
- [ ] Implement `OpenAIProvider.health_check()` by validating connectivity/auth.
- [ ] Implement `OllamaProvider.health_check()` by validating the Ollama endpoint and/or model availability.
- [ ] Update `/v1/ready` and/or `/v1/live` to reflect provider/model availability (optional but recommended for Phase 1 completion).

### Chat completion response correctness
- [ ] Align streaming contract:
  - Decide whether providers yield raw tokens or SSE chunks.
  - Make `InferenceService.stream_completion()` and providers agree.
- [ ] Populate accurate `id`, `created`, and `usage` in `app/api/chat.py` using `InferenceResponse` fields.

### Error handling and resilience
- [ ] Ensure provider exceptions are converted into `AppException` subclasses with correct codes (404/502/400).
- [ ] Add request timeout handling for provider calls.

### Tests & validation
- [ ] Expand pytest suite to cover:
  - `/v1/models`
  - `/v1/chat/completions` (stream and non-stream)
  - invalid payloads -> consistent `400` error response
  - unknown model -> consistent `404` response
  - provider unavailable -> consistent `502` response

## Summary
- The project currently has a working API scaffold, schema contracts, registry skeleton, and an orchestration service.
- Provider implementations are mock/stub-like, and API responses contain placeholder metadata.
- Completing Phase 1 requires real provider integrations, consistent streaming/usage semantics, improved health/model discovery, and end-to-end test coverage.

