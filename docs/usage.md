# Usage Guide

This guide covers everything from basic setup to advanced pipeline orchestration.

## 1. Defining Your Messages

Messages are simple `dataclasses` that represent an intent.

### Commands
Commands represent an action that changes state. They typically do not return a value.

```python
from pyline import Command
from dataclasses import dataclass

@dataclass
class RegisterUserCommand(Command):
    username: str
    email: str
```

### Queries
Queries represent a request for information. They must return a result.

```python
from pyline import Query
from dataclasses import dataclass

@dataclass
class GetUserQuery(Query):
    user_id: int
```

## 2. Implementing Handlers

Handlers contain the actual business logic.

```python
from pyline import CommandHandler, QueryHandler

class RegisterUserHandler(CommandHandler):
    async def handle(self, command: RegisterUserCommand) -> None:
        # DB logic here...
        print(f"User {command.username} registered.")

class GetUserHandler(QueryHandler):
    async def handle(self, query: GetUserQuery):
        # DB retrieval here...
        return {"id": query.user_id, "username": "alp"}
```

## 3. Using the Mediator

The mediator is the bridge between your messages and handlers.

```python
from pyline import mediator

# Registration
mediator.register_handler(RegisterUserCommand, RegisterUserHandler())
mediator.register_handler(GetUserQuery, GetUserHandler())

# Execution
async def run():
    await mediator.send(RegisterUserCommand("alp", "alp@example.com"))
    user = await mediator.send(GetUserQuery(1))
```

## 4. Advanced Pipelines

Pipelines are the most powerful feature of PyLine. They allow you to chain multiple steps.

```python
from pyline.pipe import Pipe

pipe = Pipe(
    name="Full Registration Flow",
    context={"username": "new_user", "email": "new@site.com"},
    steps=[
        RegisterUserCommand,
        GetUserQuery # Assume this takes username from context
    ]
)

await pipe.run()
```

### Automatic Result Propagation
If a step returns a result (like `GetUserQuery`), that result (if it's a dataclass or dict) is automatically merged into the pipeline's `context`. Subsequent steps can then use these new values.

## 5. Event-Driven Architecture (Event Bus)

PyLine Core includes a lightweight `EventBus` to decouple components and handle side-effects asynchronously without blocking the main execution.

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

async def run_event_bus():
    bus = EventBus()
    bus.subscribe(UserCreatedEvent, EmailNotificationHandler())
    
    # Publish event (runs in the background)
    bus.publish(UserCreatedEvent(user_id=1, name="Alp"))
    
    # Gracefully shut down and wait for all background tasks
    await bus.shutdown()
```
