from pyline import Command, Query, CommandHandler, QueryHandler
from .exceptions import HandlerNotFoundError



class HandlerMediator:
    def __init__(self):
        self.handlers = {}

    def register_handler(
        self, component: type[Command | Query], handler: CommandHandler | QueryHandler
    ):
        self.handlers[component] = handler
    
    def send(self, component: Command | Query):
        try:
            handler: CommandHandler | QueryHandler = self.handlers[component.__class__]
        except KeyError:
            raise HandlerNotFoundError(f"No handler registered for {component.__class__.__name__}")
        return handler.handle(component)
        