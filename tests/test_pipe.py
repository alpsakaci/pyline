import pytest
from dataclasses import dataclass
from typing import Any
from pyline.command import Command, CommandHandler
from pyline.query import Query, QueryResult, QueryHandler
from pyline.handler_mediator import HandlerMediator
from pyline.pipe import Pipe
from pyline.exceptions import PipelineError

@dataclass
class Step1Command(Command):
    initial_val: int

class Step1CommandHandler(CommandHandler):
    async def handle(self, command: Step1Command) -> None:
        pass # Command returns nothing, modifies state in real app, but here we just pass

@dataclass
class Step2Query(Query):
    initial_val: int

@dataclass
class Step2QueryResult(QueryResult):
    processed_val: int

class Step2QueryHandler(QueryHandler):
    async def handle(self, query: Step2Query) -> Step2QueryResult:
        return Step2QueryResult(processed_val=query.initial_val * 2)

@dataclass
class Step3Command(Command):
    processed_val: int

class Step3CommandHandler(CommandHandler):
    async def handle(self, command: Step3Command) -> None:
        pass  # Dummy handler for Step 3

class NonDataclassCommand(Command):
    pass

@pytest.fixture
def mediator() -> HandlerMediator:
    m = HandlerMediator()
    m.register_handler(Step1Command, Step1CommandHandler())
    m.register_handler(Step2Query, Step2QueryHandler())
    m.register_handler(Step3Command, Step3CommandHandler())
    return m

@pytest.mark.asyncio
async def test_pipe_execution_success(mediator: HandlerMediator):
    context: dict[str, Any] = {"initial_val": 5}
    pipe = Pipe(
        name="TestPipe",
        context=context,
        steps=[Step1Command, Step2Query, Step3Command],
        mediator=mediator
    )
    
    await pipe.run()
    
    assert context["initial_val"] == 5
    assert "processed_val" in context
    assert context["processed_val"] == 10

@pytest.mark.asyncio
async def test_pipe_raises_pipeline_error_for_non_dataclass(mediator: HandlerMediator):
    context: dict[str, Any] = {}
    pipe = Pipe(
        name="ErrorPipe",
        context=context,
        steps=[NonDataclassCommand],
        mediator=mediator
    )
    
    with pytest.raises(PipelineError) as exc_info:
        await pipe.run()
        
    assert "Step NonDataclassCommand must be a dataclass" in str(exc_info.value)

@pytest.mark.asyncio
async def test_pipe_uses_default_mediator():
    from pyline import mediator as default_mediator
    
    # We will register a dummy step to the default mediator just for this test
    @dataclass
    class DefaultMedQuery(Query):
        val: int
    
    @dataclass
    class DefaultMedQueryResult(QueryResult):
        out: int

    class DefaultMedQueryHandler(QueryHandler):
        async def handle(self, query: DefaultMedQuery) -> DefaultMedQueryResult:
            return DefaultMedQueryResult(out=query.val)
            
    default_mediator.register_handler(DefaultMedQuery, DefaultMedQueryHandler())
    
    context = {"val": 42}
    pipe = Pipe("DefaultMedPipe", context, [DefaultMedQuery])
    await pipe.run()
    
    assert context["out"] == 42
