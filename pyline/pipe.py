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

    def __init__(
        self, name: str, context: any, steps: list[Command | Query], mediator: HandlerMediator = None
    ):
        self.context: dict = context
        self.name: str = name
        self.steps: list[Command | Query] = steps
        self.mediator = mediator or default_mediator

    def context_to_params(self, step: Command | Query):
        if not is_dataclass(step):
            raise PipelineError(f"Step {step.__name__} must be a dataclass")
            
        step_keys = [f.name for f in fields(step)]
        params = {key: self.context[key] for key in step_keys if key in self.context}
        return params

    async def run(self):
        logger.info(f"Running pipe: {self.name}")
        for idx, step in enumerate(self.steps):
            logger.info(f"Running step {idx + 1} of {len(self.steps)}")
            result = await self.mediator.send(step(**self.context_to_params(step)))
            if result != None:
                self.context.update(result.__dict__)
            logger.info(f"Step {idx + 1} completed.")
        logger.info(f"Pipe {self.name} completed.")
