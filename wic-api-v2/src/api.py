from __future__ import annotations
import cwl_utils.parser as cwl_parser
from dataclasses import dataclass
from typing import Any, TypeVar, Generic, Optional
from pathlib import Path

T = TypeVar('T')

@dataclass
class IO(Generic[T]):
    name: str

@dataclass
class Process:
    # this would be dictionaries
    inputs: list[IO]
    outputs: list[IO]


class CLT(Process):
    clt_file: Optional[Path] = None
    
    def __init__(self, 
                 inputs: Optional[list[IO]] = None,
                 outputs: Optional[list[IO]] = None,
                 clt_file: Optional[Path] = None):

        if not clt_file is None:
            # TODO CHECK rely on pydantic for typechecking?
            # TODO at a minimum, better exception and wraps \
            # into PydanticError
            if not isinstance(clt_file, Path):
                raise Exception("clt_file should be a path.")
            if not clt_file.resolve().exists():
                raise FileNotFoundError()
            parsed_clt = cwl_parser.load_document_by_uri(clt_file)
            inputs = self.parse_inputs(parsed_clt.inputs)
            outputs = self.parse_outputs(parsed_clt.outputs)
        
        super().__init__(inputs, outputs)

    def parse_inputs(self, cwl_inputs: list[cwl_parser.InputParameter]):
        input_names = [inp.id.split("#")[-1] for inp in cwl_inputs]
        print(input_names)
        return [IO(name) for name in input_names]

    def parse_outputs(self, cwl_outputs: list[cwl_parser.OutputParameter]):
        output_names = [inp.id.split("#")[-1] for inp in cwl_outputs]
        print(output_names)
        return [IO(name) for name in output_names]

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