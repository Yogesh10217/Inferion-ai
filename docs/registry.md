# Model Registry Design

This document describes the structure and thread-safety details of the model metadata registry.

## Registry Interface and Classes

```mermaid
classDiagram
    class ModelMetadata {
        +str id
        +str provider
        +str display_name
        +str description
        +str version
        +int context_window
        +int max_output_tokens
        +bool supports_streaming
        +bool supports_tools
        +bool supports_images
        +bool supports_embeddings
        +str status
        +dict pricing
        +list tags
        +dict metadata
        +datetime created_at
        +datetime updated_at
    }

    class ModelRegistry {
        <<Abstract>>
        +register_model(model: ModelMetadata) ModelMetadata*
        +update_model(model_id: str, updates: dict) ModelMetadata*
        +remove_model(model_id: str)*
        +get_model(model_id: str) ModelMetadata*
        +list_models() list[ModelMetadata]*
        +model_exists(model_id: str) bool*
        +list_by_provider(provider: str) list[ModelMetadata]*
        +list_available_models() list[ModelMetadata]*
    }

    class InMemoryModelRegistry {
        -dict _models
        -RLock _lock
        +register_model()
        +update_model()
        +remove_model()
        +get_model()
        +list_models()
        +model_exists()
    }

    ModelRegistry <|-- InMemoryModelRegistry
    InMemoryModelRegistry *-- ModelMetadata
```

---

## 1. ModelMetadata Schema

The `ModelMetadata` object is a strongly typed dataclass storing key model properties (e.g. context windows, provider, features support, and current status). It automatically sets `created_at` and `updated_at` properties to timezone-aware UTC datetimes on instantiation.

---

## 2. In-Memory Registry Implementations

The primary registry implementation is the `InMemoryModelRegistry`. It manages model configurations locally using an internal dictionary.

### Thread Safety Design
Since multiple requests are served concurrently in FastAPI, registry mutation and retrieval methods are wrapped with a `threading.RLock` (re-entrant lock) context manager:
- `RLock` ensures that concurrent writes (e.g., during model discovery or manual updates) do not result in race conditions.
- Reads (e.g., model retrieval, exists checks, list queries) also acquire the `RLock` to guarantee consistency against partial updates.

### Seeding Rules
On creation, the registry seeds a set of default developer models:
1. `gpt-4o-mini`: Configured for the `openai` provider, status is `available`.
2. `llama3.1`: Configured for the `ollama` provider, status is `available`.

During startup, the application discovery process queries active providers and registers newly discovered models dynamically.
