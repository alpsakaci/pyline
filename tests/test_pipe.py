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


@pytest.mark.asyncio
async def test_pipe_logging(mediator: HandlerMediator, caplog):
    import logging
    caplog.set_level(logging.INFO)
    context: dict[str, Any] = {"val": 10}
    
    @dataclass
    class LogQuery(Query):
        val: int
        
    class LogQueryHandler(QueryHandler):
        async def handle(self, query: LogQuery) -> None: # QueryResult should really be returned, but None tests the if result is not None branch
            return None
            
    mediator.register_handler(LogQuery, LogQueryHandler())
    
    pipe = Pipe("LogPipe", context, [LogQuery], mediator=mediator)
    await pipe.run()
    
    assert "Running pipe: LogPipe" in caplog.text
    assert "Running step 1 of 1" in caplog.text
    assert "Step 1 completed." in caplog.text
    assert "Pipe LogPipe completed." in caplog.text

@pytest.mark.asyncio
async def test_pipe_missing_context_param(mediator: HandlerMediator):
    @dataclass
    class MissingParamQuery(Query):
        required_val: int
        
    class MissingParamQueryHandler(QueryHandler):
        async def handle(self, query: MissingParamQuery) -> None:
            return None
            
    mediator.register_handler(MissingParamQuery, MissingParamQueryHandler())
    
    context: dict[str, Any] = {} # Missing 'required_val'
    pipe = Pipe("MissingParamPipe", context, [MissingParamQuery], mediator=mediator)
    
    with pytest.raises(PipelineError) as exc_info:
        await pipe.run()
    assert "is missing required parameters in context: required_val" in str(exc_info.value)


@pytest.mark.asyncio
async def test_pipe_different_result_types(mediator: HandlerMediator):
    # 1. Dict result
    @dataclass
    class DictQuery(Query):
        val: int
    class DictQueryHandler(QueryHandler):
        async def handle(self, query: DictQuery) -> dict:
            return {"dict_val": query.val + 1}
            
    # 2. Slots result
    class SlotsResult:
        __slots__ = ["slots_val"]
        def __init__(self, slots_val):
            self.slots_val = slots_val
            
    @dataclass
    class SlotsQuery(Query):
        val: int
    class SlotsQueryHandler(QueryHandler):
        async def handle(self, query: SlotsQuery) -> SlotsResult:
            return SlotsResult(slots_val=query.val + 2)

    # 3. Standard result with __dict__
    class StandardResult:
        def __init__(self, dict_object_val):
            self.dict_object_val = dict_object_val
            
    @dataclass
    class StandardQuery(Query):
        val: int
    class StandardQueryHandler(QueryHandler):
        async def handle(self, query: StandardQuery) -> StandardResult:
            return StandardResult(dict_object_val=query.val + 3)

    # 4. Unsupported result type
    @dataclass
    class UnsupportedQuery(Query):
        pass
    class UnsupportedQueryHandler(QueryHandler):
        async def handle(self, query: UnsupportedQuery) -> list:
            return [1, 2, 3] # List is unsupported

    mediator.register_handler(DictQuery, DictQueryHandler())
    mediator.register_handler(SlotsQuery, SlotsQueryHandler())
    mediator.register_handler(StandardQuery, StandardQueryHandler())
    mediator.register_handler(UnsupportedQuery, UnsupportedQueryHandler())
    
    # Run pipeline with dict, slots, and standard __dict__ object
    context = {"val": 10}
    pipe = Pipe("ResultTypesPipe", context, [DictQuery, SlotsQuery, StandardQuery], mediator=mediator)
    await pipe.run()
    
    assert context["dict_val"] == 11
    assert context["slots_val"] == 12
    assert context["dict_object_val"] == 13
    
    # Run pipeline with unsupported result type
    pipe_err = Pipe("ErrorPipe", {}, [UnsupportedQuery], mediator=mediator)
    with pytest.raises(PipelineError) as exc_info:
        await pipe_err.run()
    assert "returned an unsupported result type" in str(exc_info.value)


