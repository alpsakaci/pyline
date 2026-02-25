import asyncio
from dataclasses import dataclass
from pyline import Query, QueryResult, QueryHandler, Command, CommandHandler, mediator


@dataclass
class CreateUserCommand(Command):
    name: str

class CreateUserCommandHandler(CommandHandler):
    async def handle(self, command: CreateUserCommand):
        print(f"Creating user: {command.name}")
        await asyncio.sleep(1)
        print("User created")
        # Your business logic here

@dataclass
class GetUserByNameQuery(Query):
    name: str

@dataclass
class GetUserByNameQueryResult(QueryResult):
    user: dict
    email: str

class GetUserByNameQueryHandler(QueryHandler):
    async def handle(self, query: GetUserByNameQuery):
        # Your data access logic here
        print('get user by name running')
        return GetUserByNameQueryResult(
            user={"id": 1, "name": query.name, "email": "user@example.com"},
            email="user@example.com"
        )


mediator.register_handler(CreateUserCommand, CreateUserCommandHandler())
mediator.register_handler(GetUserByNameQuery, GetUserByNameQueryHandler())


async def main():
    # Execute a command
    command = CreateUserCommand(name="John Doe")
    await mediator.send(command)

    # Execute a query
    query = GetUserByNameQuery(name="John Doe")
    result = await mediator.send(query)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
