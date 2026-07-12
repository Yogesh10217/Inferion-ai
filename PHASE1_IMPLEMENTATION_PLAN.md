# Phase 1 Implementation Plan

## Goal

Complete the Phase 1 foundation of the LLM inference engine so it becomes a usable, testable, and shareable gateway for OpenAI-compatible chat inference.

## What is already implemented

The repository already contains a strong Phase 1 foundation:

- OpenAI-compatible `/v1/chat/completions` endpoint
- Basic model registry
- SSE streaming support
- Provider abstraction layer for OpenAI and Ollama-style backends
- FastAPI route/service/schema structure
- Test coverage for routes, services, schemas, and provider behavior

## What still needs to be implemented to complete Phase 1

### 1. Real provider integration

Replace placeholder provider behavior with actual backend calls.

- Connect the OpenAI provider to the OpenAI SDK
- Connect the Ollama provider to the local Ollama HTTP API
- Use environment variables for:
  - API keys
  - provider base URLs
  - default model names

### 2. Real model discovery and registration

Make the registry reflect what is actually available.

- Seed the registry from startup configuration
- Support provider-driven model discovery
- Ensure `/v1/models` returns real, usable model entries

### 3. Provider health checks and failure handling

Make the service more reliable in production-like conditions.

- Implement `health_check()` logic per provider
- Return proper errors when a provider is unavailable
- Handle timeouts and provider exceptions gracefully

### 4. Request validation and error responses

Harden the API so invalid input is rejected cleanly.

- Validate `messages`, `model`, and stream options
- Validate common parameters like `temperature`, `max_tokens`, and `top_p`
- Return consistent JSON errors for malformed requests

### 5. Basic security and reliability

Add minimal production readiness features for Phase 1.

- Basic API key auth or request validation middleware
- Request timeout handling for provider calls
- End-to-end smoke test covering request → provider → response

## What is not required for Phase 1

These are intentionally out of scope for the first milestone:

- Temporal workflows
- continuous batching
- React dashboard
- advanced routing intelligence
- embeddings endpoint
- GPU observability stack

## Recommended implementation order

1. Make the OpenAI provider real
2. Make the Ollama provider real
3. Add provider health checks and failure handling
4. Improve validation and error responses
5. Add end-to-end smoke tests

## Suggested completion definition

Phase 1 can be considered complete when:

- a real request to `/v1/chat/completions` succeeds against a configured provider
- `/v1/models` returns valid model metadata from the active backend
- provider failures are surfaced cleanly
- tests pass for the happy path and common failure paths
