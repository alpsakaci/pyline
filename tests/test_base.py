import pytest
from pyline import Command, Query, QueryResult, CommandHandler, QueryHandler
from pyline.exceptions import PyLineError, HandlerNotFoundError, PipelineError

def test_cannot_instantiate_abstract_classes():
    with pytest.raises(TypeError):
        CommandHandler()
        
    with pytest.raises(TypeError):
        QueryHandler()

@pytest.mark.asyncio
async def test_abstract_methods_coverage():
    # To get coverage on the `pass` in abstract methods
    class CovCommandHandler(CommandHandler):
        async def handle(self, command: Command) -> None:
            return await super().handle(command)
            
    class CovQueryHandler(QueryHandler):
        async def handle(self, query: Query) -> QueryResult:
            return await super().handle(query)
            
    await CovCommandHandler().handle(None)
    await CovQueryHandler().handle(None)

def test_exceptions_inheritance():
    assert issubclass(HandlerNotFoundError, PyLineError)
    assert issubclass(PipelineError, PyLineError)
