from __future__ import annotations
import cwl_utils.parser as cwl_parser
from dataclasses import dataclass
from typing import Any, TypeVar, Generic, Optional
from pathlib import Path
from enum import Enum
import itertools


T = TypeVar('T')

class IOType(Enum):
    STRING = "string"

@dataclass
class IO(Generic[T]):
    name: str
    type: T

dataclass
class Input(IO):
    pass

class CLTInput(Input):
    def __init__(self, cwl_input: cwl_parser.InputParameter):
        name = cwl_input.id.split("#")[-1]
        type = IOType(cwl_input.type)
        super().__init__(name, type)

class Output(IO):
    pass

class CLTOutput(Output):
    def __init__(self, cwl_output: cwl_parser.OutputParameter):
        name = cwl_output.id.split("#")[-1]
        type = IOType(cwl_output.type)
        super().__init__(name, type)

@dataclass
class Process:
    # TODO CHECK type
    inputs: dict[str, Input]
    outputs: dict[str, Output]

    def load_cwl(self, cwl_file):
        # TODO CHECK rely on pydantic for typechecking?
        # TODO at a minimum, better exception and wraps \
        # into PydanticError
        if not isinstance(cwl_file, Path):
            raise Exception("clt_file should be a path.")
        if not cwl_file.resolve().exists():
            raise FileNotFoundError()
        # TODO Check what kind of exception is thrown
        return cwl_parser.load_document_by_uri(cwl_file)

class CLT(Process):
    def __init__(self, 
                 inputs: Optional[list[CLTInput]] = None,
                 outputs: Optional[list[CLTOutput]] = None,
                 clt_file: Optional[Path] = None):

        if not clt_file is None:
            # TODO CHECK or can we?
            if inputs is not None or outputs is not None :
                raise Exception("cannot have inputs or outputs definitions and a clt file")
            parsed_clt = super().load_cwl(clt_file)
            inputs = [CLTInput(cwl_input) for cwl_input in parsed_clt.inputs]
            outputs = [CLTOutput(cwl_output) for cwl_output in parsed_clt.outputs]

        if inputs is not None:
            inputs = {cwl_input.name: cwl_input for cwl_input in inputs}
        if inputs is not None:
            outputs = {cwl_output.name: cwl_output for cwl_output in outputs}

        super().__init__(inputs, outputs)

# TODO CHECK we may want to discriminate inputs and outputs
# This will depends on the step linking behavior we want to 
# implement.

@dataclass
class StepIO():
    io: IO[IOType]
    source: Optional[StepIO[IOType]] = None
    sink: Optional[StepIO[IOType]] = None
    value: Optional[IOType] = None

@dataclass
class Step():
    process: Process
    context: Optional[Workflow] = None
    scatter: Optional[list[str]] = None
    # replace with enum
    scatter_method: Optional[str] = None
    
    def __post_init__(self):
        self.inputs = { name: StepIO(io) for (name, io) in self.process.inputs.items() }
        self.outputs = { name: StepIO(io) for (name, io) in self.process.outputs.items() }
        
    def __setattr__(self, __name: str, __value: Any) -> None:
        """ Basic mechanism for linking step IO.
        
            Attributes that are not IOs or part of state management
            are stored normally.
            NOTE we may have a schema to intercept attributes that
            are allowed in cwl.
        """
        super().__setattr__(__name, __value)


class Workflow(Process):
    # steps must be duplicated and frozen
    # when creating the process inputs/outputs, those 
    # would be derived from the step actually.
    # but we should have list of names for those we want to expose 
    # to the outside world.

    def __init__(self, 
                steps: list[Step] = None,
                workflow_file: Optional[Path] = None):

        if not workflow_file is None:
            if steps is not None:
                raise Exception("cannot have steps and a clt file")
            super().load_cwl(workflow_file)

        # super().__init__(inputs, outputs)
  

    def compile(self):
        for index, step in enumerate(self.steps):
            print(f"step: {index} : {step}")