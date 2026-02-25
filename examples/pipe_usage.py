import asyncio
from dataclasses import dataclass
from typing import Any
from pyline import Command, Query, CommandHandler, QueryHandler, QueryResult, mediator
from pyline.pipe import Pipe

# 1. Define Commands, Queries, and their Handlers

@dataclass
class CreateOrderCommand(Command):
    order_id: int
    product_id: int
    quantity: int

class CreateOrderCommandHandler(CommandHandler):
    async def handle(self, command: CreateOrderCommand) -> None:
        """Commands in CQRS typically do not return values (Return type is None)."""
        print(f"📦 Creating order #{command.order_id} for product {command.product_id} (x{command.quantity})")
        # Business logic: save to DB, etc.
        await asyncio.sleep(0.1) 
        print(f"✅ Order #{command.order_id} persisted.")

@dataclass
class GetProductPriceQuery(Query):
    product_id: int

@dataclass
class PriceResult(QueryResult):
    """Queries return data that can be used by subsequent steps in the Pipe."""
    price_per_unit: float

class GetProductPriceQueryHandler(QueryHandler):
    async def handle(self, query: GetProductPriceQuery) -> PriceResult:
        print(f"� Fetching price for product {query.product_id}...")
        # Simulation: In a real app, this would be a DB lookup
        return PriceResult(price_per_unit=50.0)

@dataclass
class CalculateTotalQuery(Query):
    quantity: int
    price_per_unit: float

@dataclass
class TotalResult(QueryResult):
    total_amount: float

class CalculateTotalQueryHandler(QueryHandler):
    async def handle(self, query: CalculateTotalQuery) -> TotalResult:
        print(f"💰 Calculating total: {query.quantity} * {query.price_per_unit}")
        return TotalResult(total_amount=query.quantity * query.price_per_unit)

@dataclass
class ProcessPaymentCommand(Command):
    order_id: int
    total_amount: float

class ProcessPaymentCommandHandler(CommandHandler):
    async def handle(self, command: ProcessPaymentCommand) -> None:
        print(f"💳 Processing payment of ${command.total_amount} for Order #{command.order_id}")
        print("🎉 Payment successful!")

# 2. Register Handlers with the Mediator

mediator.register_handler(CreateOrderCommand, CreateOrderCommandHandler())
mediator.register_handler(GetProductPriceQuery, GetProductPriceQueryHandler())
mediator.register_handler(CalculateTotalQuery, CalculateTotalQueryHandler())
mediator.register_handler(ProcessPaymentCommand, ProcessPaymentCommandHandler())

# 3. Define and Run the Pipeline

async def main():
    # Initial context contains the starting parameters.
    # Note that 'order_id' is pre-generated here to follow strict CQRS for the command.
    initial_context = {
        "order_id": 1024,
        "product_id": 7,
        "quantity": 3
    }

    # The Pipe orchestrates the steps sequentially:
    # 1. CreateOrderCommand (Returns None)
    # 2. GetProductPriceQuery (Returns price_per_unit -> added to context)
    # 3. CalculateTotalQuery (Uses quantity & price_per_unit -> adds total_amount to context)
    # 4. ProcessPaymentCommand (Uses order_id & total_amount -> Returns None)
    
    order_pipeline = Pipe(
        name="Strict CQRS Order Pipeline",
        context=initial_context,
        steps=[
            CreateOrderCommand,
            GetProductPriceQuery,
            CalculateTotalQuery,
            ProcessPaymentCommand
        ]
    )

    print(f"--- Starting Pipeline: {order_pipeline.name} ---")
    await order_pipeline.run()
    print("--- Pipeline Execution Finished ---\n")
    
    print("Final Context State:")
    for key, value in order_pipeline.context.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s')
    asyncio.run(main())
