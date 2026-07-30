from typing import Any, overload, TypeVar
from pyline import Command, Query, CommandHandler, QueryHandler
from .exceptions import HandlerNotFoundError

TResult = TypeVar("TResult")


class HandlerMediator:
    """
    Mediator component that manages the registration and resolution of handlers.
    
    Acts as a central registry where Commands and Queries are mapped to their
    respective Handlers.
    """
    def __init__(self) -> None:
        self.handlers: dict[type[Command | Query[Any]], CommandHandler | QueryHandler[Any, Any]] = {}

    def register_handler(
        self,
        component: type[Command | Query[Any]],
        handler: CommandHandler | QueryHandler[Any, Any],
    ) -> None:
        """
        Registers a handler for a specific command or query type.

        Args:
            component (type[Command | Query]): The class of the command or query.
            handler (CommandHandler | QueryHandler): The handler instance to register.
        """
        self.handlers[component] = handler

    def register(self, component: type[Command | Query[Any]], *args: Any, **kwargs: Any) -> Any:
        """
        A decorator to register a handler for a specific command or query type.

        Args:
            component (type[Command | Query]): The class of the command or query.
            *args: Positional arguments to pass to the handler constructor.
            **kwargs: Keyword arguments to pass to the handler constructor.

        Returns:
            A decorator function that registers the handler.
        """
        def decorator(handler: Any) -> Any:
            if isinstance(handler, type):
                instance = handler(*args, **kwargs)
                self.register_handler(component, instance)
            else:
                self.register_handler(component, handler)
            return handler
        return decorator
    
    @overload
    async def send(self, component: Command) -> None: ...

    @overload
    async def send(self, component: Query[TResult]) -> TResult: ...

    async def send(self, component: Command | Query[Any]) -> Any:
        """
        Sends a command or query to its registered handler.

        Args:
            component (Command | Query): The command or query to execute.

        Returns:
            The result of the handler execution.

        Raises:
            HandlerNotFoundError: If no handler is registered for the component type.
        """
        try:
            handler = self.handlers[component.__class__]
        except KeyError:
            raise HandlerNotFoundError(f"No handler registered for {component.__class__.__name__}")
        if isinstance(component, Command) and isinstance(handler, CommandHandler):
            return await handler.handle(component)
        if isinstance(component, Query) and isinstance(handler, QueryHandler):
            return await handler.handle(component)
        raise HandlerNotFoundError(f"Incompatible handler for {component.__class__.__name__}")
        