# Architecture

## Overview

The backend is structured as a layered FastAPI application that separates transport concerns, application services, providers, and persistence.

## Layers

### 1. API layer

The API layer is responsible for HTTP routing and request validation. It exposes:

- /v1/health
- /v1/ready
- /v1/live
- /v1/models
- /v1/chat/completions

Route handlers remain thin and delegate work to the application service layer.

### 2. Service layer

The service layer owns business logic and orchestration for inference requests.

Responsibilities:

- validate request content
- resolve model metadata from the registry
- select and invoke providers
- return standardized response objects

### 3. Provider layer

The provider layer abstracts model backends behind an interface.

Current implementations:

- OpenAIProvider
- OllamaProvider

Each provider implements:

- generate()
- stream()
- health_check()
- list_models()

### 4. Registry layer

The registry layer stores model information in memory today, but the interface is designed so Redis or PostgreSQL can replace it later without changing the service contract.

### 5. Core utilities

Shared facilities include:

- configuration loading
- structured logging
- centralized exception handling
- middleware for request logging and error normalisation

## Request Flow

1. The client issues a request to the FastAPI router.
2. Pydantic validates the request schema.
3. The route delegates to the inference service.
4. The service validates the model and calls the selected provider.
5. The provider returns a standardized response.
6. The route transforms it into the API response or SSE stream.
7. Middleware logs the outcome and standardizes errors.

## Extensibility

The design is intentionally backend-agnostic. To add a new provider:

1. implement the abstract provider methods;
2. provide provider-specific model metadata;
3. register it in the service configuration and tests.
