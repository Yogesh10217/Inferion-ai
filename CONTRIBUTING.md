# Contributing to Inferion AI

Thank you for your interest in contributing to **Inferion AI**! We welcome contributions from developers, researchers, and AI engineers of all experience levels.

---

## 🚀 How to Contribute

### 1. Reporting Bugs & Requesting Features
- Search existing issues before creating a new one.
- Describe the bug or feature request clearly with reproducible code snippets or error logs.

### 2. Development Setup

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

### 3. Running Tests & Linting

```bash
# Run test suite
pytest -v

# Run linting and formatting
make lint
make format
```

### 4. Pull Request Process
1. Create a feature branch: `git checkout -b feat/your-feature-name`
2. Commit your changes with clear messages following conventional commits (`feat:`, `fix:`, `docs:`, `refactor:`).
3. Ensure all automated tests pass before opening a PR.
4. Submit your PR against the `main` branch with a thorough description of your changes.

---

## 📜 Code Style Guidelines
- **Python**: Follow PEP8 conventions using `Ruff` and `Black`.
- **Typing**: Use strict Python type hints (`mypy` compatible).
- **Documentation**: Provide clear docstrings for all public modules, functions, and endpoints.
