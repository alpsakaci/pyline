from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass(frozen=True, kw_only=True)
class BaseEvent(ABC):
    """Abstract base class for all events in the system."""
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_on: datetime = field(default_factory=datetime.now)