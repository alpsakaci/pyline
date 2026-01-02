from pyline import Command, Query, CommandHandler, QueryHandler


class HandlerMediator:
    def __init__(self):
        self.handlers = {}

    def register_handler(
        self, component: type[Command | Query], handler: CommandHandler | QueryHandler
    ):
        self.handlers[component] = handler
    
    async def send(self, component: Command | Query):
        handler: CommandHandler | QueryHandler = self.handlers[component.__class__]
        return await handler.handle(component)
        