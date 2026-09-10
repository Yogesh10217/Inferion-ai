# Contributing Guidelines

Thank you for contributing to the Inferion AI. This guide outlines the project's coding standards, development workflow, and pull request checklist.

## Development Setup

1. **Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -e .[dev]
   ```
3. **Configuration**:
   ```bash
   cp .env.example .env
   ```

---

## Coding Standards

### 1. Architectural Integrity
- **No Global Service State**: Do not import service singletons or instances globally. Always resolve services dynamically using FastAPI's dependency injection (`Depends`) from the application container (`request.app.state.container`).
- **Thin Transport Layer**: Keep route files in `app/api/` focused purely on protocol serialization, validation, and request state registration. Business logic must be delegated to orchestration services (e.g., `InferenceService`, `HealthService`).
- **Modular Providers**: All new LLM providers must inherit from `BaseProvider` and be registered inside `ProviderFactory._register_defaults()`.

### 2. Typing and Documentation
- **Strict Typing**: All function signatures and module-level variables must have complete type annotations. Use `from __future__ import annotations` and structure complex type references under `if TYPE_CHECKING:` blocks to avoid circular imports.
- **Docstrings**: Provide clean Google-style docstrings for every class, interface, method, and function.

### 3. Observability Rules
- **No Request Body Parsing in Middleware**: The `ObservationMiddleware` handles transport-level logging and tracking only. Endpoint handlers must populate the request state (`request.state.model`, `request.state.provider`) so the middleware can read them upon completion.
- **Custom Exceptions**: Define specific exceptions extending `AppException` rather than raising generic errors. Map new exception codes to standardized JSON outputs in `register_exception_handlers`.

---

## Running Tests

Verify your changes using `pytest` before opening a pull request:
```bash
python -m pytest
```

---

## Pull Request Checklist

Before submitting a pull request, ensure:
- [ ] All automated tests pass successfully (`python -m pytest`).
- [ ] Coverage levels have not decreased.
- [ ] No stack traces are leaked in client error payloads.
- [ ] Documentation has been updated to reflect any new modules or settings changes.
