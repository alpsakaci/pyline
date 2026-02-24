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
