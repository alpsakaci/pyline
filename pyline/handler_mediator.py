from pyline import Command, Query, CommandHandler, QueryHandler
from .exceptions import HandlerNotFoundError



class HandlerMediator:
    """
    Mediator component that manages the registration and resolution of handlers.
    
    Acts as a central registry where Commands and Queries are mapped to their
    respective Handlers.
    """
    def __init__(self):
        self.handlers = {}

    def register_handler(
        self, component: type[Command | Query], handler: CommandHandler | QueryHandler
    ):
        """
        Registers a handler for a specific command or query type.

        Args:
            component (type[Command | Query]): The class of the command or query.
            handler (CommandHandler | QueryHandler): The handler instance to register.
        """
        self.handlers[component] = handler
    
    async def send(self, component: Command | Query):
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
            handler: CommandHandler | QueryHandler = self.handlers[component.__class__]
        except KeyError:
            raise HandlerNotFoundError(f"No handler registered for {component.__class__.__name__}")
        return await handler.handle(component)
        