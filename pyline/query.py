from abc import ABC, abstractmethod


class Query(ABC):
    pass


class QueryResult(ABC):
    pass


class QueryHandler(ABC):
    @abstractmethod
    async def handle(self, query: Query) -> QueryResult:
        pass
