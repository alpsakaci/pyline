import asyncio
import signal
from dataclasses import dataclass
from pyline import BaseEvent, EventHandler, event_bus

# 1. Define an Event
@dataclass(frozen=True, kw_only=True)
class OrderProcessedEvent(BaseEvent):
    order_id: int
    total_amount: float

# 2. Define Event Handlers (Listeners)
class EmailNotificationHandler(EventHandler[OrderProcessedEvent]):
    async def handle(self, event: OrderProcessedEvent) -> None:
        print(f"📧 [Email Service] Sending confirmation for Order #{event.order_id}...")
        await asyncio.sleep(5) # Simulate network delay
        print(f"✅ [Email Service] Confirmation sent for Order #{event.order_id}.")

class InventoryUpdateHandler(EventHandler[OrderProcessedEvent]):
    async def handle(self, event: OrderProcessedEvent) -> None:
        print(f"📦 [Inventory Service] Updating stocks for Order #{event.order_id}...")
        await asyncio.sleep(0.5)
        print(f"✅ [Inventory Service] Stocks updated for Order #{event.order_id}.")

# 3. Register Subscribers
event_bus.subscribe(OrderProcessedEvent, EmailNotificationHandler())
event_bus.subscribe(OrderProcessedEvent, InventoryUpdateHandler())

async def main():
    # Signal handling: Just trigger event_bus.shutdown
    loop = asyncio.get_running_loop()
    
    # We use a Future to keep the main alive until shutdown is triggered
    shutdown_requested = loop.create_future()

    def handle_signal():
        print("\n🛑 Signal received! Triggering shutdown...")
        if not shutdown_requested.done():
            shutdown_requested.set_result(True)

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, handle_signal)
        except NotImplementedError:
            pass

    print("--- 🛒 Processing Checkout ---")
    
    event = OrderProcessedEvent(order_id=99, total_amount=249.99)
    print("🚀 Publishing OrderProcessedEvent...")
    event_bus.publish(event)
    
    print("🚶 Main flow is running. (Press Ctrl+C to stop)")
    print("Doing things... (Waiting for your command)")
    
    # Wait indefinitely until the signal handler sets the result
    await shutdown_requested
    
    # Simple call to shutdown
    print("⏳ Shutting down Event Bus...")
    await event_bus.shutdown(timeout=10.0)
    print("--- 🏁 System Shutdown ---")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
