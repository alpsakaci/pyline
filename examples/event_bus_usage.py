import asyncio
from dataclasses import dataclass
from pyline import BaseEvent, EventHandler, event_bus


# 1. Define an Event hierarchy
@dataclass(frozen=True, kw_only=True)
class OrderProcessedEvent(BaseEvent):
    order_id: int
    total_amount: float


# 2. Define Event Handlers (Listeners)
class EmailNotificationHandler(EventHandler[OrderProcessedEvent]):
    async def handle(self, event: OrderProcessedEvent) -> None:
        print(f"📧 [Email Service] Sending confirmation for Order #{event.order_id}...")
        await asyncio.sleep(1)  # Simulate network delay
        print(f"✅ [Email Service] Confirmation sent for Order #{event.order_id}.")


class InventoryUpdateHandler(EventHandler[OrderProcessedEvent]):
    async def handle(self, event: OrderProcessedEvent) -> None:
        print(f"📦 [Inventory Service] Updating stocks for Order #{event.order_id}...")
        await asyncio.sleep(0.2)
        print(f"✅ [Inventory Service] Stocks updated for Order #{event.order_id}.")


# This handler listens to the base class, demonstrating Subclass Event Propagation
class GlobalLogger(EventHandler[BaseEvent]):
    async def handle(self, event: BaseEvent) -> None:
        print(
            f"🔍 [Global Logger] Captured Event ID {event.event_id} of type: {type(event).__name__}"
        )


# 3. Register Subscribers
# Registering specific event
event_bus.subscribe(OrderProcessedEvent, EmailNotificationHandler())
event_bus.subscribe(OrderProcessedEvent, InventoryUpdateHandler())

# Registering base event
event_bus.subscribe(BaseEvent, GlobalLogger())


async def main():
    print("--- 🛒 Processing Checkout ---")

    event = OrderProcessedEvent(order_id=99, total_amount=249.99)
    print("🚀 Publishing OrderProcessedEvent...")

    # This will trigger EmailNotificationHandler, InventoryUpdateHandler, AND GlobalLogger!
    event_bus.publish(event)

    print("🚶 Main execution flow is unblocked and continues immediately...")

    # Wait for background tasks to process and then shut down gracefully
    print("⏳ Shutting down Event Bus gracefully...")
    await event_bus.shutdown(timeout=5.0)
    print("--- 🏁 System Shutdown ---")


if __name__ == "__main__":
    asyncio.run(main())
