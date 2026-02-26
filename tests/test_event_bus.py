import asyncio
import pytest
from dataclasses import dataclass
from pyline import BaseEvent, EventHandler, event_bus

@dataclass(frozen=True)
class UserCreatedEvent(BaseEvent):
    user_id: int
    username: str

class NotificationHandler(EventHandler[UserCreatedEvent]):
    def __init__(self) -> None:
        self.received_event = None
        self.call_count = 0

    async def handle(self, event: UserCreatedEvent) -> None:
        self.received_event = event
        self.call_count += 1

class AuditLogHandler(EventHandler[UserCreatedEvent]):
    def __init__(self) -> None:
        self.call_count = 0

    async def handle(self, event: UserCreatedEvent) -> None:
        await asyncio.sleep(0.1) # Simulate some async work
        self.call_count += 1

@pytest.mark.asyncio
async def test_event_bus_pub_sub():
    # Setup
    # Reset event_bus to a clean state for testing if it's singleton-like
    # But usually it's better to create a new instance for unit tests
    from pyline.event_bus import EventBus
    bus = EventBus()
    
    handler1 = NotificationHandler()
    handler2 = AuditLogHandler()
    
    bus.subscribe(UserCreatedEvent, handler1)
    bus.subscribe(UserCreatedEvent, handler2)
    
    # Action
    event = UserCreatedEvent(user_id=1, username="alp")
    bus.publish(event)
    
    # Wait for completion
    await bus.wait_for_completion()
    
    # Assert
    assert handler1.call_count == 1
    assert handler1.received_event == event
    assert handler2.call_count == 1

@pytest.mark.asyncio
async def test_event_bus_error_isolation(caplog):
    from pyline.event_bus import EventBus
    bus = EventBus()
    
    class FailingHandler(EventHandler[UserCreatedEvent]):
        async def handle(self, event: UserCreatedEvent) -> None:
            raise ValueError("Something went wrong")

    success_handler = NotificationHandler()
    
    bus.subscribe(UserCreatedEvent, FailingHandler())
    bus.subscribe(UserCreatedEvent, success_handler)
    
    event = UserCreatedEvent(user_id=2, username="beta")
    bus.publish(event)
    
    await bus.wait_for_completion()
    
    # Success handler should still be called
    assert success_handler.call_count == 1
    # Error should be logged
    assert "Error in event handler FailingHandler" in caplog.text

@pytest.mark.asyncio
async def test_event_bus_shutdown():
    from pyline.event_bus import EventBus
    bus = EventBus()
    
    handler = NotificationHandler()
    bus.subscribe(UserCreatedEvent, handler)
    
    await bus.shutdown()
    
    # After shutdown, new events should be ignored
    event = UserCreatedEvent(user_id=3, username="gamma")
    bus.publish(event)
    
    # wait_for_completion should return instantly as no tasks are created
    await bus.wait_for_completion()
    
    assert handler.call_count == 0

@pytest.mark.asyncio
async def test_event_bus_wait_no_tasks():
    from pyline.event_bus import EventBus
    bus = EventBus()
    # Should return instantly and not raise anything
    await bus.wait_for_completion()

@pytest.mark.asyncio
async def test_event_bus_timeout_cancellation():
    from pyline.event_bus import EventBus
    bus = EventBus()
    
    class SlowHandler(EventHandler[UserCreatedEvent]):
        def __init__(self):
            self.cancelled = False
        async def handle(self, event: UserCreatedEvent) -> None:
            try:
                await asyncio.sleep(1.0)
            except asyncio.CancelledError:
                self.cancelled = True
                raise

    handler = SlowHandler()
    bus.subscribe(UserCreatedEvent, handler)
    bus.publish(UserCreatedEvent(user_id=4, username="slow"))
    
    # Wait with short timeout
    await bus.wait_for_completion(timeout=0.1)
    
    # The task should have been cancelled by the refined shutdown logic
    assert handler.cancelled is True

@pytest.mark.asyncio
async def test_event_bus_drain_nested_events():
    from pyline.event_bus import EventBus
    bus = EventBus()
    
    @dataclass(frozen=True, kw_only=True)
    class ChildEvent(BaseEvent):
        pass

    class ParentHandler(EventHandler[UserCreatedEvent]):
        async def handle(self, event: UserCreatedEvent) -> None:
            bus.publish(ChildEvent())

    class ChildHandler(EventHandler[ChildEvent]):
        def __init__(self):
            self.handled = False
        async def handle(self, event: ChildEvent) -> None:
            await asyncio.sleep(0.05)
            self.handled = True

    child_handler = ChildHandler()
    bus.subscribe(UserCreatedEvent, ParentHandler())
    bus.subscribe(ChildEvent, child_handler)
    
    bus.publish(UserCreatedEvent(user_id=5, username="parent"))
    
    # wait_for_completion should drain the child event too
    await bus.wait_for_completion()
    
    assert child_handler.handled is True

@pytest.mark.asyncio
async def test_event_bus_timeout_immediate_break(caplog):
    from pyline.event_bus import EventBus
    bus = EventBus()
    
    class ForeverHandler(EventHandler[UserCreatedEvent]):
        async def handle(self, event: UserCreatedEvent) -> None:
            await asyncio.sleep(10)

    bus.subscribe(UserCreatedEvent, ForeverHandler())
    bus.publish(UserCreatedEvent(user_id=6, username="forever"))
    
    # Using a 0 timeout should trigger the early break in the loop
    await bus.wait_for_completion(timeout=0)
    assert "Graceful shutdown timed out" in caplog.text
    assert len(bus._background_tasks) == 0

@pytest.mark.asyncio
async def test_event_handler_abc_coverage():
    from pyline.event_handler import EventHandler
    
    class ConcreteHandler(EventHandler[UserCreatedEvent]):
        async def handle(self, event: UserCreatedEvent) -> None:
            await super().handle(event) # Covers the 'pass' in ABC

    handler = ConcreteHandler()
    await handler.handle(UserCreatedEvent(user_id=7, username="abc"))
