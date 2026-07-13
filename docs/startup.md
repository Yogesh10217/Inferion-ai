# Application Startup Lifecycle

This document describes the application initialization lifecycle, dependency setup, and provider discovery during startup.

## Lifespan Context Manager

The FastAPI application orchestrates start and shutdown phases using an asynchronous `lifespan` context manager in [main.py](file:///c:/Users/Yogesh E/OneDrive/Desktop/Manjus/llm-inference-engine/app/main.py#L15).

```
[Start App] ──► Create ServiceContainer ──► Run InfrastructureInitializer ──► [Server Ready]
                                                                                   │
[Graceful Shutdown] ◄── Release Resources ◄── Log Shutdown Info ◄─── Receive SIGTERM
```

---

## Startup Sequence

1. **ServiceContainer Initialization**:
   - The settings are loaded from environment variables.
   - The thread-safe `InMemoryModelRegistry` is instantiated and seeded with default developer models.
   - Singleton service instances for logging, `ProviderFactory`, `RequestRouter`, `InferenceService`, `MetricsService`, and `HealthService` are instantiated.
   - The startup timestamp is set.

2. **Infrastructure Initialization**:
   - The lifespan method runs the [InfrastructureInitializer](file:///c:/Users/Yogesh E/OneDrive/Desktop/Manjus/llm-inference-engine/app/core/initializer.py#L10).
   - **Provider Health Check**: The initializer polls each registered provider (`openai`, `ollama`) to verify base connectivity.
   - **Model Discovery**: The initializer queries each provider's `list_models()` method to discover available model assets dynamically.
   - **Registry Seeding**: Discovered models are registered directly into the `ModelRegistry`.
   - **Summary Logging**: Outputs a detailed, formatted startup summary showing configuration, active providers, and registered models.
