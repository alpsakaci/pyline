from abc import ABC, abstractmethod


class Command(ABC):
    """Abstract base class for all commands."""
    pass


class CommandHandler(ABC):
    """Abstract base class for command handlers."""
    
    @abstractmethod
    async def handle(self, command: Command) -> None:
        """
        Handles the execution of a command.

        Args:
            command (Command): The command to handle.
        """
        pass
