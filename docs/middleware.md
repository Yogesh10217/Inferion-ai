# Observability Middleware

This document describes the design, correlation tracing, and logging structure of the HTTP middleware.

## Middleware Architecture

The transport-level logging, latency checking, and request ID routing are handled cleanly in `ObservationMiddleware` (inheriting from Starlette's `BaseHTTPMiddleware`).

```
Request ──► [ObservationMiddleware] ──► [FastAPI Route / Inference]
                                                   │
Response ◄── [Add X-Request-ID Header] ◄───────────┘
```

The middleware handles only transport-level properties. It does not parse the request JSON body to extract provider/model, avoiding latency overhead and body parsing errors. Instead, the inference route handler registers the provider and model dynamically to the request state, which is read by the middleware during log production on request completion.

---

## Observability Responsibilities

### 1. Request ID Generation (Correlation ID)
Every request passing through the middleware is assigned a Request ID:
- If the incoming request has an `x-request-id` header, that value is preserved.
- Otherwise, a new UUID is generated.
- The ID is stored in `request.state.request_id` for downstream route utilization and added to the outgoing response headers as `X-Request-ID`.

### 2. Latency Tracing
The middleware captures high-resolution start times using `time.perf_counter()`. After downstream request resolution, the total delta is calculated, converted to milliseconds, and recorded.

### 3. Metrics Compilation
The middleware registers the request counts and latencies into the container's thread-safe `MetricsService` upon completion. Unhandled exceptions or status codes >= 400 are recorded as errors.

---

## Log Output Structure

Structured JSON logs are output to standard stdout/stderr for log aggregators (e.g. Datadog, ELK).

### Structured Log Fields
Every log event contains:
- `timestamp` (ISO-8601 UTC string)
- `request_id` (UUID string)
- `method` (HTTP method name, e.g., `POST`, `GET`)
- `endpoint` (API route path, e.g., `/v1/chat/completions`)
- `provider` (LLM provider name, e.g., `openai` — if resolved)
- `model` (model ID, e.g., `gpt-4o-mini` — if resolved)
- `latency_ms` (float, rounded to 3 decimal places)
- `status_code` (integer status code)
- `client_ip` (IP string of the calling client)
- Optional `error_code`/`error_message` fields on exceptions.
