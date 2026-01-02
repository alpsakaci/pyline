from abc import ABC
from dataclasses import fields, is_dataclass
from pyline.command import Command
from pyline.query import Query
from pyline import mediator as default_mediator
from .handler_mediator import HandlerMediator
from .exceptions import PipelineError
import logging

logger = logging.getLogger(__name__)

class Pipe(ABC):
    """
    Orchestrates a sequence of Commands and Queries.

    Executes a list of steps sequentially, sharing a context dictionary between them.
    Output of one step (QueryResult) can be input to the next step.
    """

    def __init__(
        self, name: str, context: any, steps: list[Command | Query], mediator: HandlerMediator = None
    ):
        """
        Initializes a new Pipe.

        Args:
            name (str): The name of the pipeline (for logging).
            context (dict): Initial shared context data.
            steps (list[Command | Query]): List of Command/Query classes (not instances) to execute.
            mediator (HandlerMediator, optional): The mediator instance to use. 
                                                  Defaults to the global mediator.
        """
        self.context: dict = context
        self.name: str = name
        self.steps: list[Command | Query] = steps
        self.mediator = mediator or default_mediator

    def context_to_params(self, step: Command | Query):
        """
        Maps context data to the parameters of a step (dataclass).

        Args:
            step (Command | Query): The step class to prepare parameters for.

        Returns:
            dict: A dictionary of parameters extracted from the context.

        Raises:
            PipelineError: If the step is not a dataclass.
        """
        if not is_dataclass(step):
            raise PipelineError(f"Step {step.__name__} must be a dataclass")
            
        step_keys = [f.name for f in fields(step)]
        params = {key: self.context[key] for key in step_keys if key in self.context}
        return params

    async def run(self):
        """
        Executes the pipeline steps sequentially.
        
        Logs progress and execution details. Updates context with results from steps.
        """
        logger.info(f"Running pipe: {self.name}")
        for idx, step in enumerate(self.steps):
            logger.info(f"Running step {idx + 1} of {len(self.steps)}")
            result = await self.mediator.send(step(**self.context_to_params(step)))
            if result != None:
                self.context.update(result.__dict__)
            logger.info(f"Step {idx + 1} completed.")
        logger.info(f"Pipe {self.name} completed.")
