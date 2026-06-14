import asyncio
import logging
from typing import Type, Dict, List, Any
from .base_event import BaseEvent
from .event_handler import EventHandler

logger = logging.getLogger(__name__)

class EventBus:
    """
    Background event bus implementation using the Publish/Subscribe pattern.
    
    Allows multiple handlers to subscribe to the same event type. Events are 
    dispatched asynchronously without blocking the main execution flow.
    """
    def __init__(self) -> None:
        self._subscribers: Dict[Type[BaseEvent], List[EventHandler[Any]]] = {}
        self._background_tasks: set[asyncio.Task[Any]] = set()
        self._is_shutting_down: bool = False

    def subscribe(self, event_type: Type[BaseEvent], handler: EventHandler[Any]) -> None:
        """
        Subscribes a handler to a specific event type.

        Args:
            event_type (Type[BaseEvent]): The class of the event to listen for.
            handler (EventHandler): The handler instance to register.
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def publish(self, event: BaseEvent) -> None:
        """
        Publishes an event to all registered subscribers in the background.
        Supports triggering handlers subscribed to parent classes of the event.

        Args:
            event (BaseEvent): The event instance to publish.
        """
        if self._is_shutting_down:
            logger.warning(f"Event {event.__class__.__name__} ignored. EventBus is shutting down.")
            return

        event_type = type(event)
        handlers_to_run = []
        seen_handlers = set()

        for registered_type, handlers in self._subscribers.items():
            if issubclass(event_type, registered_type):
                for handler in handlers:
                    if handler not in seen_handlers:
                        seen_handlers.add(handler)
                        handlers_to_run.append(handler)

        for handler in handlers_to_run:
            task = asyncio.create_task(self._run_handler(handler, event))
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)

    async def shutdown(self, timeout: float | None = None) -> None:
        """
        Initiates a graceful shutdown of the event bus.
        Stops accepting new events and waits for pending ones.
        """
        self._is_shutting_down = True
        await self.wait_for_completion(timeout=timeout)

    async def wait_for_completion(self, timeout: float | None = None) -> None:
        """
        Waits for all pending background tasks to complete.
        Implemented as a 'drain' mechanism to handle nested events.

        Args:
            timeout (float, optional): Maximum total time to wait in seconds.
                                       If None, waits indefinitely.
        """
        if not self._background_tasks:
            return

        start_time = asyncio.get_event_loop().time()
        
        while self._background_tasks:
            remaining_timeout = None
            if timeout is not None:
                elapsed = asyncio.get_event_loop().time() - start_time
                remaining_timeout = max(0, timeout - elapsed)
                if remaining_timeout <= 0:
                    break

            logger.info(f"Waiting for {len(self._background_tasks)} background tasks to complete...")
            _, pending = await asyncio.wait(self._background_tasks, timeout=remaining_timeout)
            
            if pending and timeout is not None:
                # If we still have pending tasks and we reached the timeout
                break

        if self._background_tasks:
            logger.warning(
                f"Graceful shutdown timed out. {len(self._background_tasks)} tasks still running. "
                "Cancelling remaining tasks for clean exit..."
            )
            # Explicitly cancel remaining tasks to trigger cleanup logic
            for task in self._background_tasks:
                task.cancel()
            
            # Briefly wait for cancellation to propagate
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
            logger.info("Remaining tasks cancelled.")
        else:
            logger.info("All background tasks completed gracefully.")

    async def _run_handler(self, handler: EventHandler[Any], event: BaseEvent) -> None:
        """
        Executes a single handler and catches potential errors to prevent 
        the event loop from crashing.
        """
        try:
            logger.debug(f"Executing handler {handler.__class__.__name__} for event {event.__class__.__name__}")
            await handler.handle(event)
        except Exception as e:
            logger.error(f"Error in event handler {handler.__class__.__name__}: {str(e)}", exc_info=True)