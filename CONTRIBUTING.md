# Contributing to Inferion AI

Thank you for your interest in contributing to **Inferion AI**! We welcome contributions from developers, researchers, and AI engineers of all experience levels.

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before participating — we are committed to a welcoming, harassment-free community.

---

## 🚀 How to Contribute

### 1. Reporting Bugs

Use the [🐛 Bug Report](.github/ISSUE_TEMPLATE/bug_report.md) issue template.
- Search existing issues before opening a new one.
- Include a minimal reproduction, your environment details, and the full error/stack trace.

### 2. Requesting Features

Use the [🚀 Feature Request](.github/ISSUE_TEMPLATE/feature_request.md) issue template.
- Describe the motivation and the component it affects.
- If you have a proposed API design, include it.

### 3. Development Setup

```bash
# Fork & Clone repository
git clone https://github.com/Yogesh10217/Inferion-ai.git
cd Inferion-ai

# Set up virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

### 4. Running Tests & Linting

```bash
# Run full test suite with coverage report
pytest -v --cov=app --cov-report=term-missing --cov-fail-under=60

# Run linting and formatting checks
make lint
make format
```

> **CI enforces**: Black formatting, Ruff linting, `pip-audit` security scan, and ≥ 60% code coverage.
> All checks must pass before a PR will be merged.

### 5. Pull Request Process

1. Create a feature branch: `git checkout -b feat/your-feature-name`
2. Commit your changes with clear messages following [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` — new feature
   - `fix:` — bug fix
   - `docs:` — documentation only
   - `refactor:` — code restructuring, no behaviour change
   - `test:` — adding or fixing tests
   - `ci:` — CI/CD changes
3. Ensure all CI checks pass before opening a PR.
4. Open your PR against the `main` branch using the [PR template](.github/PULL_REQUEST_TEMPLATE.md).
5. Link the relevant issue with `Closes #NNN` in the PR description.

---

## 📜 Code Style Guidelines

- **Python**: PEP 8 conventions enforced by `Ruff` and `Black` (line length: 120).
- **Typing**: Use strict Python type hints (`mypy`-compatible) for all public functions and class attributes.
- **Documentation**: Provide clear docstrings for all public modules, functions, and endpoints.
- **Tests**: Every new feature or bug fix must be accompanied by a test. Add tests in the `tests/` directory mirroring the module path.

---

## 🏗️ Project Layout

```
app/           # All backend source code (94+ modules)
tests/         # Mirrors app/ structure with unit & integration tests
docs/          # Deep-dive documentation per subsystem
deploy/        # Helm charts, Kubernetes manifests, DR scripts
.github/       # CI/CD workflows, issue templates, PR template
```

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
