from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

TResult = TypeVar("TResult")
TQuery = TypeVar("TQuery", bound="Query[Any]")


class Query(Generic[TResult], ABC):
    """Abstract base class for all queries."""
    pass


class QueryResult(ABC):
    """Abstract base class for all query results."""
    pass


class QueryHandler(Generic[TQuery, TResult], ABC):
    """Abstract base class for query handlers."""

    @abstractmethod
    async def handle(self, query: TQuery) -> TResult:
        """
        Handles the execution of a query.

        Args:
            query (TQuery): The query to handle.

        Returns:
            TResult: The result of the query.
        """
        pass
