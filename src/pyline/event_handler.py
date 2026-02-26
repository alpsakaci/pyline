from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from .base_event import BaseEvent

TEvent = TypeVar("TEvent", bound=BaseEvent)

class EventHandler(ABC, Generic[TEvent]):
    """
    Abstract base class for all event handlers (listeners).
    
    Handlers process events asynchronously and are typically executed in the background.
    """

    @abstractmethod
    async def handle(self, event: TEvent) -> None:
        """
        Handles the event.

        Args:
            event (TEvent): The event to handle.
        """
        pass
