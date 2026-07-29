# OpenTelemetry Distributed Tracing (Phase 4.3)

The **LLM Inference Engine** implements enterprise-grade, low-overhead distributed tracing using W3C Trace Context and OpenTelemetry semantic standards.

---

## Architecture Overview

```
   [ Incoming HTTP Request ]
               │ (W3C traceparent)
               ▼
      TracingMiddleware  ──────► Root Span: HTTP POST /v1/chat/completions
               │
      ┌────────┴────────┐
      ▼                 ▼
Routing Span    Inference Span ───► Plugin Child Spans
      │                 │
      ▼                 ▼
 BatchSpanProcessor (Non-blocking Background Queue)
      │
      ▼
 ExporterRegistry ───► (Console / OTLP HTTP / OTLP gRPC / Jaeger / Zipkin)
```

---

## Span Hierarchy & Semantic Conventions

Root HTTP spans capture request lifecycle metadata and nest child spans across subsystem boundaries:

- `HTTP POST /v1/chat/completions` (Root Span)
  - `routing.decision` (Child Span)
  - `inference.execution` (Child Span)
    - `plugin.execution.metrics_logger` (Child Span)
  - `db.query` (Child Span)

### Core Trace Attributes
- `service.name`: `llm-inference-engine`
- `llm.provider`: Provider ID (`openai_provider`, `anthropic_provider`)
- `llm.model`: Model identifier (`gpt-4`, `claude-3-5-sonnet`)
- `llm.usage.prompt_tokens`: Number of prompt tokens
- `llm.usage.completion_tokens`: Number of completion tokens
- `organization.id`: Organization identifier
- `request.id`: Unique request UUID

---

## Sampler Configurations

Tracing supports 5 dynamic Head Sampling modes:
1. **`AlwaysOnSampler`**: Samples 100% of traces (default for dev/debug).
2. **`AlwaysOffSampler`**: Suppresses all trace collection.
3. **`ParentBasedSampler`**: Respects incoming upstream W3C sampling flags (`01` = sampled).
4. **`TraceIdRatioBasedSampler`**: Deterministic percentage sampling based on MD5 hashing of `trace_id`.
5. **`OrganizationOverrideSampler`**: Organization-specific sampling overrides.

---

## Exporter Setup & Configuration

Configure exporters via Admin REST APIs or environment variables:

```bash
# OTLP Collector (HTTP)
POST /v1/tracing/exporters {"name": "otlp_http"}

# Jaeger Setup
POST /v1/tracing/exporters {"name": "jaeger"}
```

### Supported Exporters
- `console`: Prints JSON span representations to STDOUT.
- `otlp_http`: Exports OpenTelemetry protocol over HTTP (`http://localhost:4318/v1/traces`).
- `otlp_grpc`: Exports OpenTelemetry protocol over gRPC (`localhost:4317`).
- `jaeger`: Exports to Jaeger Collector (`http://localhost:14268/api/traces`).
- `zipkin`: Exports to Zipkin Collector (`http://localhost:9411/api/v2/spans`).

---

## Admin REST APIs

- `GET /v1/tracing/config`: Get active tracer config (environment, service name, active exporter).
- `PUT /v1/tracing/config`: Update tracing settings (change exporter, dynamic sample ratio, environment).
- `GET /v1/tracing/exporters`: List available and active exporters.
- `POST /v1/tracing/exporters`: Switch active span exporter.
- `GET /v1/tracing/sampling`: Retrieve current sampler configuration.
