# LLM Inference Engine — Architecture Overview

This document summarizes the backend architecture scaffold that has been created so far for the LLM Inference Engine project.

## Goal

The current implementation establishes the foundation for a production-ready FastAPI-based backend that can later evolve into a full inference platform with providers, model routing, and service orchestration.

## Current Status

The repository now contains a working FastAPI application skeleton with:

- a FastAPI app factory
- OpenAPI/Swagger documentation
- CORS middleware
- environment-based configuration loading
- logging setup
- centralized exception handling
- API routers for health, models, and chat
- provider abstractions
- an in-memory model registry
- a service layer placeholder
- smoke tests for the basic endpoints

## Project Structure

```text
app/
    main.py

    api/
        chat.py
        models.py
        health.py

    providers/
        base_provider.py
        openai_provider.py
        ollama_provider.py

    registry/
        model_registry.py

    services/
        inference_service.py

    schemas/
        request.py
        response.py

    core/
        config.py
        logger.py
        exceptions.py

tests/
```

## Core Components

### 1. Application Entry Point
File: [app/main.py](app/main.py)

The application entry point creates the FastAPI instance using an app factory pattern. It wires together:

- CORS support
- global exception handling middleware
- router registration for the API endpoints
- a simple root endpoint

This design makes it easier to test and extend the application later.

### 2. API Layer
Files:
- [app/api/health.py](app/api/health.py)
- [app/api/models.py](app/api/models.py)
- [app/api/chat.py](app/api/chat.py)

The API layer contains the HTTP-facing routes:

- /v1/health: returns a service health status
- /v1/models: returns available registered models
- /v1/chat/completions: exposes a placeholder chat-completion endpoint

This separation keeps the HTTP concerns isolated from the business logic.

### 3. Schemas
Files:
- [app/schemas/request.py](app/schemas/request.py)
- [app/schemas/response.py](app/schemas/response.py)

Pydantic models define the request and response shapes for the API. They give the app a clear contract for incoming data and outgoing payloads.

### 4. Providers
Files:
- [app/providers/base_provider.py](app/providers/base_provider.py)
- [app/providers/openai_provider.py](app/providers/openai_provider.py)
- [app/providers/ollama_provider.py](app/providers/ollama_provider.py)

Providers represent external or internal inference backends. The abstract base class defines the interface that every provider should implement.

At this stage, the provider implementations are placeholders, but they are structured so that real integrations can be added later.

### 5. Registry
File: [app/registry/model_registry.py](app/registry/model_registry.py)

The model registry is an in-memory registry that stores available models. It currently seeds a couple of example entries:

- gpt-4o-mini -> openai
- llama3.1 -> ollama

This gives the system a simple model catalog for the initial phase.

### 6. Service Layer
File: [app/services/inference_service.py](app/services/inference_service.py)

The service layer is the orchestration point between the API layer and provider/registry pieces. It is currently a placeholder that will later handle the actual inference workflow.

### 7. Core Infrastructure
Files:
- [app/core/config.py](app/core/config.py)
- [app/core/logger.py](app/core/logger.py)
- [app/core/exceptions.py](app/core/exceptions.py)

These files provide the shared application foundation:

- configuration loading from environment variables
- logging configuration
- app-specific exceptions
- a centralized exception response pattern

## How the Flow Works Today

1. The FastAPI app is created from [app/main.py](app/main.py).
2. The app includes routers from the API package.
3. Requests arrive at the API endpoints.
4. The endpoints use schemas for input/output structure.
5. The service layer and providers are ready to be extended for actual inference work.
6. The registry exposes basic model metadata for the current phase.

## Why This Structure Is Useful

This scaffold follows a clean separation of concerns:

- API layer: HTTP and routing
- Services: orchestration and business logic coordination
- Providers: backend-specific integrations
- Registry: model metadata and discovery
- Core: shared infrastructure and cross-cutting concerns

This makes the codebase easier to test, evolve, and maintain as the project grows.

## Testing

A small smoke test suite has been added in [tests/test_health.py](tests/test_health.py).

It verifies that:

- the health endpoint responds successfully
- the models endpoint responds successfully

## Verification

The current scaffold has been verified by running:

```bash
py -3.10 -m pytest tests/test_health.py -q
```

Result:

- 2 tests passed

## Next Evolution Path

The next phase can expand this foundation by adding:

- dependency injection for services and providers
- real provider integrations with OpenAI and Ollama
- streaming chat completions
- authentication and rate limiting
- more sophisticated model routing
- Temporal workflow integration

## Summary

What exists today is a clean, extensible backend skeleton that can serve as the starting point for a full LLM inference platform. It is deliberately structured to support future production features without prematurely coupling the app to a single implementation detail.
