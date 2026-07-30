import pytest
from dataclasses import dataclass
from pyline import Command, Query, QueryResult, CommandHandler, QueryHandler
from pyline.handler_mediator import HandlerMediator
from pyline.exceptions import HandlerNotFoundError

@dataclass
class DummyCommand(Command):
    data: str

class DummyCommandHandler(CommandHandler):
    async def handle(self, command: DummyCommand) -> None:
        pass  # Dummy command does nothing for test

@dataclass
class DummyQuery(Query):
    req: str

@dataclass
class DummyQueryResult(QueryResult):
    res: str

class DummyQueryHandler(QueryHandler):
    async def handle(self, query: DummyQuery) -> DummyQueryResult:
        return DummyQueryResult(res=f"reply to {query.req}")

@dataclass
class UnregisteredCommand(Command):
    pass

@pytest.fixture
def mediator() -> HandlerMediator:
    return HandlerMediator()

@pytest.mark.asyncio
async def test_register_and_send_command(mediator: HandlerMediator):
    handler = DummyCommandHandler()
    mediator.register_handler(DummyCommand, handler)
    
    cmd = DummyCommand(data="test")
    result = await mediator.send(cmd)
    
    assert result is None

@pytest.mark.asyncio
async def test_register_and_send_query(mediator: HandlerMediator):
    handler = DummyQueryHandler()
    mediator.register_handler(DummyQuery, handler)
    
    query = DummyQuery(req="test")
    result = await mediator.send(query)
    
    assert isinstance(result, DummyQueryResult)
    assert result.res == "reply to test"

@pytest.mark.asyncio
async def test_send_unregistered_component_raises_error(mediator: HandlerMediator):
    cmd = UnregisteredCommand()
    
    with pytest.raises(HandlerNotFoundError) as exc_info:
        await mediator.send(cmd)
    
    assert "No handler registered for UnregisteredCommand" in str(exc_info.value)

@pytest.mark.asyncio
async def test_send_incompatible_handler_raises_error(mediator: HandlerMediator):
    # Registering a Command with a QueryHandler (shouldn't happen in normal use but covered for safety)
    mediator.register_handler(DummyCommand, DummyQueryHandler()) # type: ignore
    
    with pytest.raises(HandlerNotFoundError) as exc_info:
        await mediator.send(DummyCommand(data="test"))
        
    assert "Incompatible handler for DummyCommand" in str(exc_info.value)


@pytest.mark.asyncio
async def test_register_decorator(mediator: HandlerMediator):
    @mediator.register(DummyCommand)
    class DecoratedHandler(CommandHandler):
        def __init__(self):
            self.called = False
        async def handle(self, command: DummyCommand) -> None:
            self.called = True
            
    cmd = DummyCommand(data="decorator_test")
    handler = mediator.handlers[DummyCommand]
    assert isinstance(handler, DecoratedHandler)
    
    await mediator.send(cmd)
    assert handler.called is True


@pytest.mark.asyncio
async def test_register_decorator_non_class(mediator: HandlerMediator):
    handler = DummyCommandHandler()
    decorator = mediator.register(DummyCommand)
    decorated = decorator(handler)
    
    assert decorated is handler
    assert mediator.handlers[DummyCommand] is handler


@pytest.mark.asyncio
async def test_register_decorator_with_dependency_kwargs(mediator: HandlerMediator):
    class MockRepository:
        def __init__(self):
            self.saved_data = []

        def save(self, data: str):
            self.saved_data.append(data)

    repo = MockRepository()

    @mediator.register(DummyCommand, repository=repo)
    class InjectableHandler(CommandHandler):
        def __init__(self, repository: MockRepository):
            self.repository = repository

        async def handle(self, command: DummyCommand) -> None:
            self.repository.save(command.data)

    cmd = DummyCommand(data="repo_test")
    await mediator.send(cmd)

    assert repo.saved_data == ["repo_test"]


@pytest.mark.asyncio
async def test_register_decorator_with_dependency_args(mediator: HandlerMediator):
    class MockRepository:
        def __init__(self):
            self.saved_data = []

        def save(self, data: str):
            self.saved_data.append(data)

    repo = MockRepository()

    @mediator.register(DummyCommand, repo)
    class InjectableHandler(CommandHandler):
        def __init__(self, repository: MockRepository):
            self.repository = repository

        async def handle(self, command: DummyCommand) -> None:
            self.repository.save(command.data)

    cmd = DummyCommand(data="positional_test")
    await mediator.send(cmd)

    assert repo.saved_data == ["positional_test"]



