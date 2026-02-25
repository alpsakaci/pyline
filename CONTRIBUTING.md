# Contributing to PyLine

Thank you for your interest in contributing to PyLine!

## Development Setup

1. Clone the repository.
2. Create a virtual environment: `python -m venv venv`.
3. Install dependencies: `pip install -e .`.
4. Install development tools: `pip install pytest pytest-asyncio pytest-cov black mypy pre-commit`.

## Standards

- **Formatting**: We use `black` for code formatting.
- **Typing**: All core logic must be strictly typed using `mypy`.
- **Testing**: Maintain 100% code coverage. Run tests with `pytest`.

## Pull Request Process

1. Ensure all tests pass.
2. Update `CHANGELOG.md` if applicable.
3. Submit your PR for review.
