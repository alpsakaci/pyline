# Welcome to PyLine Core

PyLine Core is a lightweight, type-safe Python micro-framework designed to simplify the implementation of the **Command Query Responsibility Segregation (CQRS)** pattern and **Pipeline Orchestration**.

## Why PyLine Core?

In implementation-heavy projects, logic often becomes scattered and difficult to test. PyLine Core provides a structured foundation that:

- **Decouples Logic**: Commands and Queries are separated from their execution logic.
- **Enforces Type Safety**: Leverages modern Python type hints and overloads for a superior developer experience.
- **Simplifies Orchestration**: Pipelines allow you to chain operations with automatic state management.
- **Event-Driven Architecture**: Powerful background `EventBus` with Publish/Subscribe support and graceful shutdown.
- **Maintains Leaness**: Zero external runtime dependencies in the core package.

## Core Concepts

### Mediator Pattern
The `HandlerMediator` acts as a central post office. You register handlers for specific message types (Commands or Queries), and the mediator ensures they reach their destination.

### Pipelines
The `Pipe` component allows you to define a sequence of steps. Each step can be a Command or a Query. The pipeline handles:
1. **Context Management**: A shared dictionary passed between steps.
2. **Auto-Mapping**: Context keys are automatically mapped to step parameters.
3. **Result Collection**: Results from Queries are automatically merged back into the shared context.

### Event Bus (Publish/Subscribe)
The `EventBus` allows components to broadcast events (like `UserCreatedEvent`) to multiple background handlers asynchronously, decoupling side-effects from your main business logic.

## Navigation
- [Get Started](usage.md)
- [Architecture Deep-Dive](architecture.md)
- [API Reference](api.md)
