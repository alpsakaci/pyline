# Changelog

All notable changes to this project will be documented in this file.

## [3.1.0] - 2026-06-14
### Changed
- Bumped package version to `3.1.0`.

## [3.0.0] - 2026-02-26
### Added
- Background `EventBus` implementation using the Publish/Subscribe pattern.
- `BaseEvent` and `EventHandler` abstract base classes.
- Graceful shutdown and nested event handling capabilities for the Event Bus.
- Package version updated to `3.0.0`.


## [2.2.1] - 2026-02-25
### Changed
- Refactored to `src-layout` for better package isolation.
- Relocated `main.py` to `examples/simple_usage.py`.
- Updated package version to `2.2.1`.

### Added
- Comprehensive test suite (100% coverage).
- `CONTRIBUTING.md` and `CHANGELOG.md`.
- `pyproject.toml`, `.editorconfig`, and `.pre-commit-config.yaml`.
- Type overloads for `HandlerMediator`.
