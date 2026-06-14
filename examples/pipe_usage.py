import asyncio
from dataclasses import dataclass
from typing import Any
from pyline import Command, Query, CommandHandler, QueryHandler, QueryResult, mediator
from pyline.pipe import Pipe
from pyline.exceptions import PipelineError

# 1. Define Commands, Queries, and their Handlers with decorator registration


@dataclass
class CreateOrderCommand(Command):
    order_id: int
    product_id: int
    quantity: int


@mediator.register(CreateOrderCommand)
class CreateOrderCommandHandler(CommandHandler):
    async def handle(self, command: CreateOrderCommand) -> None:
        """Commands in CQRS typically do not return values (Return type is None)."""
        print(
            f"📦 Creating order #{command.order_id} for product {command.product_id} (x{command.quantity})"
        )
        # Business logic: save to DB, etc.
        await asyncio.sleep(0.1)
        print(f"✅ Order #{command.order_id} persisted.")


@dataclass
class PriceResult(QueryResult):
    """Queries return data that can be used by subsequent steps in the Pipe."""
    price_per_unit: float


@dataclass
class GetProductPriceQuery(Query[PriceResult]):
    product_id: int


@mediator.register(GetProductPriceQuery)
class GetProductPriceQueryHandler(QueryHandler[GetProductPriceQuery, PriceResult]):
    async def handle(self, query: GetProductPriceQuery) -> PriceResult:
        print(f"🔍 Fetching price for product {query.product_id}...")
        # Simulation: In a real app, this would be a DB lookup
        return PriceResult(price_per_unit=50.0)


@dataclass
class TotalResult(QueryResult):
    total_amount: float


@dataclass
class CalculateTotalQuery(Query[TotalResult]):
    quantity: int
    price_per_unit: float


@mediator.register(CalculateTotalQuery)
class CalculateTotalQueryHandler(QueryHandler[CalculateTotalQuery, TotalResult]):
    async def handle(self, query: CalculateTotalQuery) -> TotalResult:
        print(f"💰 Calculating total: {query.quantity} * {query.price_per_unit}")
        return TotalResult(total_amount=query.quantity * query.price_per_unit)


@dataclass
class ProcessPaymentCommand(Command):
    order_id: int
    total_amount: float


@mediator.register(ProcessPaymentCommand)
class ProcessPaymentCommandHandler(CommandHandler):
    async def handle(self, command: ProcessPaymentCommand) -> None:
        print(
            f"💳 Processing payment of ${command.total_amount} for Order #{command.order_id}"
        )
        print("🎉 Payment successful!")


# 2. Define and Run the Pipeline


async def main():
    # Initial context contains the starting parameters.
    # Note that 'order_id' is pre-generated here to follow strict CQRS for the command.
    initial_context = {"order_id": 1024, "product_id": 7, "quantity": 3}

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
            ProcessPaymentCommand,
        ],
    )

    print(f"--- Starting Pipeline: {order_pipeline.name} ---")
    await order_pipeline.run()
    print("--- Pipeline Execution Finished ---\n")

    print("Final Context State:")
    for key, value in order_pipeline.context.items():
        print(f"  {key}: {value}\n")

    # 3. Demonstrate PipelineError validation for missing parameters
    print("--- Testing Pipeline parameter validation ---")
    bad_context = {"product_id": 7}  # Missing 'order_id' and 'quantity'
    invalid_pipeline = Pipe(
        name="Invalid Pipeline",
        context=bad_context,
        steps=[CreateOrderCommand],
    )
    try:
        await invalid_pipeline.run()
    except PipelineError as e:
        print(f"Successfully caught expected error: {e}")


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s")
    asyncio.run(main())
