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
Queries represent a request for information. They must return a result of a specific type by inheriting from `Query[TResult]`.

```python
from pyline import Query
from dataclasses import dataclass

@dataclass
class GetUserQuery(Query[dict]):
    user_id: int
```

## 2. Implementing Handlers

Handlers contain the actual business logic. Query handlers inherit from `QueryHandler[TQuery, TResult]`.

```python
from pyline import CommandHandler, QueryHandler

class RegisterUserHandler(CommandHandler):
    async def handle(self, command: RegisterUserCommand) -> None:
        # DB logic here...
        print(f"User {command.username} registered.")

class GetUserHandler(QueryHandler[GetUserQuery, dict]):
    async def handle(self, query: GetUserQuery) -> dict:
        # DB retrieval here...
        return {"id": query.user_id, "username": "alp"}
```

## 3. Using the Mediator

The mediator is the bridge between your messages and handlers. You can register handlers either by decorating them with `@mediator.register` or registering them manually.

### Decorator Registration (Recommended)

```python
from pyline import mediator

@mediator.register(RegisterUserCommand)
class RegisterUserHandler(CommandHandler):
    async def handle(self, command: RegisterUserCommand) -> None:
        pass

@mediator.register(GetUserQuery)
class GetUserHandler(QueryHandler[GetUserQuery, dict]):
    async def handle(self, query: GetUserQuery) -> dict:
        return {"id": query.user_id}
```

### Dependency Injection via Decorator

Dependencies (such as repositories, services, or configurations) can be passed directly into `@mediator.register(...)` as positional or keyword arguments. They will be passed to the handler's constructor:

```python
user_repo = UserRepository()

@mediator.register(RegisterUserCommand, repository=user_repo)
class RegisterUserHandler(CommandHandler):
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def handle(self, command: RegisterUserCommand) -> None:
        await self.repository.save(command.username, command.email)
```

### Manual Registration

```python
user_repo = UserRepository()
mediator.register_handler(RegisterUserCommand, RegisterUserHandler(repository=user_repo))
mediator.register_handler(GetUserQuery, GetUserHandler())
```

### Execution

```python
async def run():
    # mediator.send is fully typed and knows RegisterUserCommand returns None
    await mediator.send(RegisterUserCommand("alp", "alp@example.com"))
    
    # mediator.send is fully typed and knows GetUserQuery returns a dict
    user = await mediator.send(GetUserQuery(1))
```
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
If a step returns a result, it is automatically merged into the pipeline's `context`. Subsequent steps can then use these new values. The result can be of the following types:
- A dictionary (`dict`)
- A dataclass (safely serialized)
- Any standard Python object containing `__dict__`
- Any memory-optimized Python object using `__slots__`

If a step returns any other type or if required arguments for a step are missing from the `context`, a `PipelineError` will be fırst raised to help you debug quickly.

## 5. Event-Driven Architecture (Event Bus)

PyLine Core includes a lightweight `EventBus` to decouple components and handle side-effects asynchronously without blocking the main execution.

### Subclass Subscription Support
The `EventBus` supports subclass propagation. This means if you subscribe a handler to a base event class (such as `BaseEvent`), it will automatically trigger for all published subclasses of that event type:

```python
from pyline import BaseEvent, EventHandler, EventBus
from dataclasses import dataclass
import asyncio

@dataclass(frozen=True, kw_only=True)
class UserCreatedEvent(BaseEvent):
    user_id: int
    name: str

# EmailNotificationHandler listens to UserCreatedEvent
class EmailNotificationHandler(EventHandler[UserCreatedEvent]):
    async def handle(self, event: UserCreatedEvent) -> None:
        print(f"Sending welcome email to User {event.user_id} ({event.name})")

# GeneralLogger listens to all system events inheriting from BaseEvent
class GeneralLogger(EventHandler[BaseEvent]):
    async def handle(self, event: BaseEvent) -> None:
        print(f"Logging event {event.event_id} of type {type(event).__name__}")

async def run_event_bus():
    bus = EventBus()
    bus.subscribe(UserCreatedEvent, EmailNotificationHandler())
    bus.subscribe(BaseEvent, GeneralLogger())  # Will also catch UserCreatedEvent!
    
    # Publish event (runs in the background)
    bus.publish(UserCreatedEvent(user_id=1, name="Alp"))
    
    # Gracefully shut down and wait for all background tasks
    await bus.shutdown()
```
