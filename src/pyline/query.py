from abc import ABC, abstractmethod


class Query(ABC):
    """Abstract base class for all queries."""
    pass


class QueryResult(ABC):
    """Abstract base class for all query results."""
    pass


class QueryHandler(ABC):
    """Abstract base class for query handlers."""

    @abstractmethod
    async def handle(self, query: Query) -> QueryResult:
        """
        Handles the execution of a query.

        Args:
            query (Query): The query to handle.

        Returns:
            QueryResult: The result of the query.
        """
        pass
