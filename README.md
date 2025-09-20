# PyLine Core

A lightweight Python framework for implementing the Command Query Responsibility Segregation (CQRS) pattern with pipeline orchestration capabilities.

## Overview

PyLine Core provides a clean architecture for building applications using the CQRS pattern, where commands and queries are separated, and handlers are managed through a mediator pattern. The framework also includes a pipeline system for orchestrating complex workflows.

## Features

- **Command Pattern**: Separate command objects from their handlers
- **Query Pattern**: Dedicated query objects with result types
- **Mediator Pattern**: Centralized handler registration and execution
- **Pipeline Orchestration**: Chain commands and queries in sequential workflows
- **Type Safety**: Built with Python type hints for better IDE support
- **Minimal Dependencies**: Lightweight with no external dependencies

## Installation

```bash
pip install pyline-core
```

## Quick Start

### 1. Define Commands and Handlers

```python
from pyline import Command, CommandHandler
from dataclasses import dataclass

@dataclass
class CreateUserCommand(Command):
    name: str

class CreateUserCommandHandler(CommandHandler):
    def handle(self, command: CreateUserCommand):
        print(f"Creating user: {command.name}")
        # Your business logic here
```

### 2. Define Queries and Handlers

```python
from pyline import Query, QueryResult, QueryHandler
from dataclasses import dataclass

@dataclass
class GetUserByNameQuery(Query):
    name: str

@dataclass
class GetUserByNameQueryResult(QueryResult):
    user: dict
    email: str

class GetUserByNameQueryHandler(QueryHandler):
    def handle(self, query: GetUserByNameQuery):
        # Your data access logic here
        return GetUserByNameQueryResult(
            user={"id": 1, "name": query.name, "email": "user@example.com"},
            email="user@example.com"
        )
```

### 3. Register Handlers

```python
from pyline import mediator

mediator.register_handler(CreateUserCommand, CreateUserCommandHandler())
mediator.register_handler(GetUserByNameQuery, GetUserByNameQueryHandler())
```

### 4. Execute Commands and Queries

```python
# Execute a command
command = CreateUserCommand(name="John Doe")
mediator.send(command)

# Execute a query
query = GetUserByNameQuery(name="John Doe")
result = mediator.send(query)
print(f"User email: {result.email}")
```

## Pipeline Orchestration

PyLine Core includes a powerful pipeline system for orchestrating complex workflows:

```python
from pyline.pipe import Pipe

# Define a pipeline
create_user_pipe = Pipe(
    name="Create User Pipeline",
    context={
        "name": "John Doe",
    },
    steps=[
        CreateUserCommand,
        GetUserByNameQuery,
        # Add more commands/queries as needed
    ],
)

# Execute the pipeline
create_user_pipe.run()
```

### Pipeline Features

- **Context Sharing**: Data flows between pipeline steps through a shared context
- **Automatic Parameter Mapping**: Pipeline automatically maps context data to command/query parameters
- **Result Propagation**: Query results are automatically added to the context for subsequent steps
- **Step Tracking**: Built-in logging shows progress through pipeline execution

## Architecture

### Core Components

1. **Command**: Abstract base class for commands
2. **CommandHandler**: Abstract base class for command handlers
3. **Query**: Abstract base class for queries
4. **QueryResult**: Abstract base class for query results
5. **QueryHandler**: Abstract base class for query handlers
6. **HandlerMediator**: Central registry and dispatcher for handlers
7. **Pipe**: Pipeline orchestration system

### Design Patterns

- **Command Pattern**: Encapsulates requests as objects
- **Query Pattern**: Separates read operations from write operations
- **Mediator Pattern**: Centralizes communication between components
- **Pipeline Pattern**: Orchestrates sequential execution of operations

## Requirements

- Python 3.10+

## License

This project is licensed under the terms specified in the LICENSE file.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

**Alp Sakaci**  
Email: alp@alpsakaci.com
