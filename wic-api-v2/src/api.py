from __future__ import annotations
from dataclasses import dataclass
from typing import Any, TypeVar, Generic, Optional

T = TypeVar('T')

@dataclass
class IO(Generic[T]):
    name: str

@dataclass
class Process:
    # this would be dictionaries
    inputs: list[IO]
    outputs: list[IO]

@dataclass
class CLT(Process):
    pass

@dataclass
class StepIO(Generic[T]):
    io: IO
    source: Optional[StepIO[T]] = None
    sink: Optional[StepIO[T]] = None
    value: Optional[T] = None


@dataclass
class Step():
    process: Process
    context: Optional[Workflow] = None
    scatter: Optional[list[str]] = None
    # replace with enum
    scatter_method: Optional[str] = None
    
    def __post_init__(self):
        self.inputs : list[StepIO] = []
        self.outputs : list[StepIO] = []
        for input in self.process.inputs:
            self.inputs.append(StepIO(input))
        for output in self.process.outputs:
            self.outputs.append(StepIO(output))
        
    def __setattr__(self, __name: str, __value: Any) -> None:
        """ Basic mechanism for linking step IO.
        
            Attributes that are not IOs or part of state management
            are stored normally.
            NOTE we may have a schema to intercept attributes that
            are allowed in cwl.
        """
        super().__setattr__(__name, __value)

    def __getattribute__(self, __name: str) -> Any:
        """Basic mechanism for linking step IO."""
        super().__getattribute__(__name)

@dataclass
class Workflow(Process):
    # steps must be duplicated and frozen
    # when creating the process inputs/outputs, those 
    # would be derived from the step actually.
    # but we should have list of names for those we want to expose 
    # to the outside world.
    steps: list[Step]
    scatter: Optional[bool] = False

    def compile(self):
        for index, step in enumerate(self.steps):
            print(f"step: {index} : {step}")