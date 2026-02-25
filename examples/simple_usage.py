from pyline import Command, CommandHandler
from dataclasses import dataclass
import asyncio

@dataclass
class CreateUserCommand(Command):
    name: str

class CreateUserCommandHandler(CommandHandler):
    async def handle(self, command: CreateUserCommand):
        print(f"Creating user: {command.name}")
        await asyncio.sleep(1)
        print("User created")
        # Your business logic here


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
    async def handle(self, query: GetUserByNameQuery):
        # Your data access logic here
        print('get user by name running')
        return GetUserByNameQueryResult(
            user={"id": 1, "name": query.name, "email": "user@example.com"},
            email="user@example.com"
        )

from pyline import mediator

mediator.register_handler(CreateUserCommand, CreateUserCommandHandler())
mediator.register_handler(GetUserByNameQuery, GetUserByNameQueryHandler())


import asyncio

async def main():
    # Execute a command
    tasks = []
    command = CreateUserCommand(name="John Doe")
    tasks.append(mediator.send(command))

    # Execute a query
    query = GetUserByNameQuery(name="John Doe")
    tasks.append(mediator.send(query))

    create_user_result, get_user_result = await asyncio.gather(*tasks)
    print(get_user_result)

if __name__ == "__main__":
    asyncio.run(main())
