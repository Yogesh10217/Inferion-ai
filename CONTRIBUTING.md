# Contributing

Thank you for contributing to the LLM Inference Engine project.

## Development Setup

```bash
python -m venv .venv
. .venv/bin/activate  # On Windows use .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## Running Tests

```bash
pytest -q
```

## Code Style

- Keep routes thin and delegate to services.
- Prefer small, focused modules.
- Use type hints and docstrings.
- Add tests for all new functionality.

## Pull Request Checklist

- [ ] Tests pass locally
- [ ] New functionality has corresponding tests
- [ ] Docs are updated where needed
- [ ] No breaking API changes unless intentionally documented

## Reporting Issues

Please open an issue with:

- a clear description
- steps to reproduce
- expected behavior
- actual behavior
