from __future__ import annotations
import cwl_utils.parser as cwl_parser
from dataclasses import dataclass
from typing import Any, TypeVar, Generic, Optional
from pathlib import Path
from enum import Enum


T = TypeVar('T')

class IOType(Enum):
    STRING = "string"
@dataclass
class IO(Generic[T]):
    name: str
    type: IOType

class Input(IO):
    def __init__(self, cwl_input: cwl_parser.InputParameter):
        name = cwl_input.id.split("#")[-1]
        type = IOType(cwl_input.type)
        super().__init__(name, type)

class Output(IO):
    def __init__(self, cwl_output: cwl_parser.OutputParameter):
        name = cwl_output.id.split("#")[-1]
        type = IOType(cwl_output.type)
        super().__init__(name, type)


@dataclass
class Process:
    # TODO CHECK type
    inputs: dict[str, IO]
    outputs: dict[str, IO]

class CLT(Process):
    clt_file: Optional[Path] = None
    
    def __init__(self, 
                 inputs: Optional[list[Input]] = None,
                 outputs: Optional[list[Output]] = None,
                 clt_file: Optional[Path] = None):

        if not clt_file is None:
            # TODO CHECK or can we?
            if inputs is not None or outputs is not None :
                raise Exception("cannot have inputs or outputs definitions and a clt file")
            # TODO CHECK rely on pydantic for typechecking?
            # TODO at a minimum, better exception and wraps \
            # into PydanticError
            if not isinstance(clt_file, Path):
                raise Exception("clt_file should be a path.")
            if not clt_file.resolve().exists():
                raise FileNotFoundError()
            parsed_clt = cwl_parser.load_document_by_uri(clt_file)
            inputs = [Input(cwl_input) for cwl_input in parsed_clt.inputs]
            outputs = [Output(cwl_output) for cwl_output in parsed_clt.outputs]

        if inputs is not None:
            inputs = {cwl_input.name: cwl_input for cwl_input in inputs}
        if inputs is not None:
            outputs = {cwl_output.name: cwl_output for cwl_output in outputs}

        super().__init__(inputs, outputs)

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
        # TODO CHECK Can we declared as member as 
        # and initialize here?
        # switch to dictionaries
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