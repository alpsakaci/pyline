# Architecture & Patterns

PyLine Core is built on proven software engineering patterns to ensure maintainability and testability at scale.

## Command Query Responsibility Segregation (CQRS)

By separating "writes" (Commands) from "reads" (Queries), PyLine allows you to optimize each path independently. 

- **Commands**: Encapsulate the "what" and "how" of state changes.
- **Queries**: Encapsulate the "what" of data retrieval.

## The Mediator Pattern

The `HandlerMediator` centralizes communication. Instead of components depending on dozens of handlers, they only depend on the `mediator`. This reduces coupling and makes it trivial to swap handler implementations without changing the call site.

## Pipeline Orchestration

The `Pipe` component implements a sequential orchestration pattern. It is particularly useful for complex business transactions that involve multiple discrete steps.

### Context Isolation
Each pipeline run has its own isolated `context`. This ensures that concurrent pipeline executions do not interfere with each other.

### Parameter Mapping Strategy
PyLine uses Python's `dataclasses.fields` to inspect the requirements of each step. It then safely extracts matching keys from the pipeline context. This prevents "prop drilling" where you have to manually pass every parameter through a chain of functions.

## Event-Driven Architecture (Publish/Subscribe)

The `EventBus` provides a mechanism for decoupling components via asynchronous events. 

### Background Execution
When an event is published via `bus.publish()`, registered `EventHandler`s are executed in background tasks using `asyncio.create_task()`. This ensures that publishing an event never blocks the main execution flow, making it ideal for side-effects like sending emails or tracking metrics.

### Graceful Shutdown
The event bus tracks pending background tasks and provides a `shutdown()` method to "drain" these tasks, with optional timeout support. This ensures your application can exit cleanly without losing critical background events.

## Type Safety & Overloads

PyLine heavily uses Python's typing system. The `mediator.send` method uses `@overload` to provide precise return types:
- Sending a `Command` returns `None`.
- Sending a generic `Query[TResult]` returns `TResult`.

This ensures that your IDE can catch potential bugs before you even run the code.
