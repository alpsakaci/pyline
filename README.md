# PyLine Core

[![CI](https://github.com/alpsakaci/pyline/actions/workflows/ci.yml/badge.svg)](https://github.com/alpsakaci/pyline/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3100/)

A lightweight Python framework for implementing the Command Query Responsibility Segregation (CQRS) pattern with pipeline orchestration capabilities.

## Key Features

- **CQRS Implementation**: Strong separation between Commands (write) and Queries (read).
- **Mediator Pattern**: Decouple components with a centralized handler registration.
- **Pipeline Orchestration**: Execute sequences of steps with a shared context, robust output type mapping, and automatic parameter validation.
- **Event-Driven Architecture**: Powerful background `EventBus` with Publish/Subscribe, subclass event propagation, and graceful shutdown.
- **Type-Safe**: Modern Python type hints with generic queries and `@overload` support for superior developer experience.
- **Micro-Framework**: Ultra-lightweight with zero external dependencies in core.

## Installation

```bash
pip install pyline-core
```

## Quick Start

### 1. Define Components and Register Handlers

Use the `@mediator.register` decorator to map Commands and Queries to their respective Handlers. Define the expected return type for Queries by inheriting from `Query[TResult]`.

```python
from pyline import Command, Query, CommandHandler, QueryHandler, mediator
from dataclasses import dataclass

@dataclass
class CreateUserCommand(Command):
    name: str

@mediator.register(CreateUserCommand)
class CreateUserCommandHandler(CommandHandler):
    async def handle(self, command: CreateUserCommand) -> None:
        print(f"Creating user: {command.name}")

@dataclass
class GetUserQuery(Query[dict]):
    name: str

@mediator.register(GetUserQuery)
class GetUserQueryHandler(QueryHandler[GetUserQuery, dict]):
    async def handle(self, query: GetUserQuery) -> dict:
        return {"id": 1, "name": query.name}
```

### 2. Execute Messages

```python
# Execution
async def main():
    # mediator.send is fully type-safe and returns None for Commands
    await mediator.send(CreateUserCommand(name="Alp"))
    
    # mediator.send knows GetUserQuery returns a dict
    user = await mediator.send(GetUserQuery(name="Alp"))
    print(user)
```

## Advanced: Pipeline Orchestration

Chain multiple commands and queries into a single workflow with shared context. Results from steps (dicts, dataclasses, objects with `__dict__` or `__slots__`) are automatically mapped and merged back into the context:

```python
from pyline.pipe import Pipe

pipe = Pipe(
    name="Registration Flow",
    context={"name": "John Doe"},
    steps=[CreateUserCommand, GetUserQuery]
)

# Throws a descriptive PipelineError if required context parameters are missing
await pipe.run()
```

## Event-Driven Architecture (Event Bus)

PyLine Core includes a lightweight `EventBus` supporting subclass propagation to decouple components and handle side-effects asynchronously:

```python
from pyline import BaseEvent, EventHandler, EventBus
from dataclasses import dataclass
import asyncio

@dataclass(frozen=True, kw_only=True)
class UserCreatedEvent(BaseEvent):
    user_id: int
    name: str

# EmailNotificationHandler listens specifically to UserCreatedEvent
class EmailNotificationHandler(EventHandler[UserCreatedEvent]):
    async def handle(self, event: UserCreatedEvent) -> None:
        print(f"Sending welcome email to User {event.user_id} ({event.name})")

# GeneralLogger listens to all events inheriting from BaseEvent
class GeneralLogger(EventHandler[BaseEvent]):
    async def handle(self, event: BaseEvent) -> None:
        print(f"Logging event {event.event_id} of type {type(event).__name__}")

async def main():
    bus = EventBus()
    bus.subscribe(UserCreatedEvent, EmailNotificationHandler())
    bus.subscribe(BaseEvent, GeneralLogger())  # Will also trigger for UserCreatedEvent!
    
    # Publish event (runs in the background)
    bus.publish(UserCreatedEvent(user_id=1, name="Alp"))
    
    # Gracefully shut down and wait for all background tasks
    await bus.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

## Documentation

For detailed guides and full API reference, visit our documentation site (coming soon).

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for local development setup and standards.

## License

MIT. See [LICENSE](LICENSE) for details.
