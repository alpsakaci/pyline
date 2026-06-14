import asyncio
from dataclasses import dataclass
from pyline import Query, QueryResult, QueryHandler, Command, CommandHandler, mediator


@dataclass
class CreateUserCommand(Command):
    name: str


@mediator.register(CreateUserCommand)
class CreateUserCommandHandler(CommandHandler):
    async def handle(self, command: CreateUserCommand) -> None:
        print(f"Creating user: {command.name}")
        await asyncio.sleep(1)
        print("User created")


@dataclass
class GetUserByNameQueryResult(QueryResult):
    user: dict
    email: str


@dataclass
class GetUserByNameQuery(Query[GetUserByNameQueryResult]):
    name: str


@mediator.register(GetUserByNameQuery)
class GetUserByNameQueryHandler(QueryHandler[GetUserByNameQuery, GetUserByNameQueryResult]):
    async def handle(self, query: GetUserByNameQuery) -> GetUserByNameQueryResult:
        print("get user by name running")
        return GetUserByNameQueryResult(
            user={"id": 1, "name": query.name, "email": "user@example.com"},
            email="user@example.com",
        )


async def main():
    # Execute a command
    command = CreateUserCommand(name="John Doe")
    await mediator.send(command)

    # Execute a query (fully type-safe: result is inferred as GetUserByNameQueryResult)
    query = GetUserByNameQuery(name="John Doe")
    result = await mediator.send(query)
    print(f"Result type: {type(result).__name__}")
    print(f"User dict: {result.user}")
    print(f"Email: {result.email}")


if __name__ == "__main__":
    asyncio.run(main())
