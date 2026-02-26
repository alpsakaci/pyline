# PyLine Core

[![CI](https://github.com/alpsakaci/pyline/actions/workflows/ci.yml/badge.svg)](https://github.com/alpsakaci/pyline/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3100/)

A lightweight Python framework for implementing the Command Query Responsibility Segregation (CQRS) pattern with pipeline orchestration capabilities.

## 🚀 Key Features

- **CQRS Implementation**: Strong separation between Commands (write) and Queries (read).
- **Mediator Pattern**: Decouple components with a centralized handler registration.
- **Pipeline Orchestration**: Execute sequences of steps with a shared context and automatic parameter mapping.
- **Event-Driven Architecture**: Powerful background `EventBus` with Publish/Subscribe support and graceful shutdown.
- **Type-Safe**: Modern Python type hints with `@overload` support for superior developer experience.
- **Micro-Framework**: Ultra-lightweight with zero external dependencies in core.

## 📦 Installation

```bash
pip install pyline-core
```

## 🚥 Quick Start

### 1. Define Components

```python
from pyline import Command, Query, CommandHandler, QueryHandler
from dataclasses import dataclass

@dataclass
class CreateUserCommand(Command):
    name: str

class CreateUserCommandHandler(CommandHandler):
    async def handle(self, command: CreateUserCommand) -> None:
        print(f"Creating user: {command.name}")

@dataclass
class GetUserQuery(Query):
    name: str

class GetUserQueryHandler(QueryHandler):
    async def handle(self, query: GetUserQuery):
        return {"id": 1, "name": query.name}
```

### 2. Register and Execute

```python
from pyline import mediator

# Registration
mediator.register_handler(CreateUserCommand, CreateUserCommandHandler())
mediator.register_handler(GetUserQuery, GetUserQueryHandler())

# Execution
async def main():
    await mediator.send(CreateUserCommand(name="Alp"))
    user = await mediator.send(GetUserQuery(name="Alp"))
    print(user)
```

## 🛠 Advanced: Pipeline Orchestration

Chain multiple commands and queries into a single workflow with shared context:

```python
from pyline.pipe import Pipe

pipe = Pipe(
    name="Registration Flow",
    context={"name": "John Doe"},
    steps=[CreateUserCommand, GetUserQuery]
)

await pipe.run()
```

## 📻 Event-Driven Architecture (Event Bus)

PyLine Core includes a lightweight `EventBus` to decouple components and handle side-effects asynchronously without blocking the main execution:

```python
from pyline import BaseEvent, EventHandler, EventBus
from dataclasses import dataclass
import asyncio

@dataclass(frozen=True, kw_only=True)
class UserCreatedEvent(BaseEvent):
    user_id: int
    name: str

class EmailNotificationHandler(EventHandler[UserCreatedEvent]):
    async def handle(self, event: UserCreatedEvent) -> None:
        print(f"Sending welcome email to User {event.user_id} ({event.name})")

async def main():
    bus = EventBus()
    bus.subscribe(UserCreatedEvent, EmailNotificationHandler())
    
    # Publish event (runs in the background)
    bus.publish(UserCreatedEvent(user_id=1, name="Alp"))
    
    # Gracefully shut down and wait for all background tasks
    await bus.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

## 📖 Documentation

For detailed guides and full API reference, visit our documentation site (coming soon).

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for local development setup and standards.

## 📄 License

MIT. See [LICENSE](LICENSE) for details.
