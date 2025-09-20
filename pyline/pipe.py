from abc import ABC
from dataclasses import fields
from pyline.command import Command
from pyline.query import Query
from pyline import mediator

class Pipe(ABC):

    def __init__(
        self, name: str, context: any, steps: list[Command | Query]
    ):
        self.context: dict = context
        self.name: str = name
        self.steps: list[Command | Query] = steps

    def context_to_params(self, step: Command | Query):
        step_keys = [f.name for f in fields(step)]
        params = (self.context[key] for key in step_keys if key in self.context)
        return params

    def run(self):
        print(f"Running pipe: {self.name}")
        for idx, step in enumerate(self.steps):
            print(f"Running step {idx + 1} of {len(self.steps)}")
            result = mediator.send(step(*self.context_to_params(step)))
            if result != None:
                self.context.update(result.__dict__)
            print(f"Step {idx + 1} completed.")
        print(f"Pipe {self.name} completed.")
