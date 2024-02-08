from __future__ import annotations
import cwl_utils.parser as cwl_parser
from dataclasses import dataclass
from typing import Any, TypeVar, Generic, Optional
from pathlib import Path
from enum import Enum
from urllib.parse import urlparse


T = TypeVar('T')

class IOType(str, Enum):
    STRING = "string",
    FILE = "File"

@dataclass
class IO(Generic[T]):
    name: str
    type: T

dataclass
class Input(IO):
    pass

# TODO All cwl IO have name and type encoded the same way so maybe we could 
# have a factory to create IO from them and factor the code there.
class CLTInput(Input):
    def __init__(self, cwl_input: cwl_parser.InputParameter):
        name = cwl_input.id.split("#")[-1]
        type = IOType(cwl_input.type)
        super().__init__(name, type)

class WorkflowInput(Input):
    def __init__(self, cwl_input: cwl_parser.WorkflowInputParameter):
        name = cwl_input.id.split("#")[-1]
        type = IOType(cwl_input.type)
        # TODO REMOVE
        # for step in steps:
        #     for input in step.inputs:
        #         if input:
        #             self.source = input
            
        super().__init__(name, type)

class Output(IO):
    pass

class CLTOutput(Output):
    def __init__(self, cwl_output: cwl_parser.OutputParameter):
        name = cwl_output.id.split("#")[-1]
        type = IOType(cwl_output.type)
        super().__init__(name, type)

class WorkflowOutput(Output):
    def __init__(self, cwl_output: cwl_parser.WorkflowOutputParameter):
        name = cwl_output.id.split("#")[-1]
        type = IOType(cwl_output.type)
        super().__init__(name, type)
        self.outputSource = cwl_output.outputSource.split("#")[-1]

@dataclass
class Process:
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

        # TODO CHECK if casting to Input and Output is ok
        # TODO CHECK how pydantic manages that for serialization
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

    # TODO CHECK Maybe all those should be factory methods,
    # and we try to leave the model as lean as possible.
    def __init__(self, 
                steps: list[Step] = None,
                workflow_file: Optional[Path] = None):

        if not workflow_file is None:
            if steps is not None:
                raise Exception("cannot have steps and a clt file")
            parsed_workflow = super().load_cwl(workflow_file)

            # workflows inputs / outputs
            inputs = [WorkflowInput(cwl_input) for cwl_input in parsed_workflow.inputs]
            outputs = [WorkflowOutput(cwl_output) for cwl_output in parsed_workflow.outputs]
            inputs = {cwl_input.name: cwl_input for cwl_input in inputs}
            outputs = {cwl_output.name: cwl_output for cwl_output in outputs}

            # workflow steps
            steps = {}
            for cwl_step in parsed_workflow.steps:
                step_name = cwl_step.id.split("#")[-1]
                # TODO CHECK that this cover all cases
                cwl_file = Path(urlparse(cwl_step.run).path)
                # TODO CHECK parsed twice, we could just load the yaml
                parsed_process = super().load_cwl(cwl_file)
                # TODO check if we can have a better test
                # TODO deal with exception
                if parsed_process.class_ == "Workflow":
                    process = Workflow(workflow_file=cwl_file)
                if parsed_process.class_ == "CommandLineTool":
                    process = CLT(clt_file=cwl_file)
                steps[step_name] = Step(process)

            # TODO for each step, check every in :
            # - if in is another step output remember and link them afterwards
            # - if in is a workflow input, we need to create a indirection so when we
            #   link this input, we are actually checking we can link
            # TODO for each step, check every out:
            # - every out should have a source that is a step. we need to create
            # so the workflow output becomes the sink.

            # connect workflow inputs to stepIO
            for cwl_step in parsed_workflow.steps:
                for cwl_step_input in cwl_step.in_:
                    (cwl_step_name, cwl_step_input_name) = cwl_step_input.id.split("#")[-1].split('/')
                    cwl_step_input_source = cwl_step_input.source.split("#")[-1]
                    input = inputs.get(cwl_step_input_source)
                    #if we have a step connected to a workflow input
                    if input:
                        input.step_io = steps[cwl_step_name].inputs[cwl_step_input_name]

            for output in outputs.values():
                for cwl_step_output in cwl_step.out:
                    if cwl_step_output.split("#")[-1] == output.outputSource:
                        (cwl_step_name, cwl_step_output) = output.outputSource.split("/")
                        steps[cwl_step_name].outputs[cwl_step_output].sink = output
                        print(f"outputSource : {output.outputSource}")
        
        self.steps = steps
        super().__init__(inputs, outputs)
  

    def compile(self):
        for index, step in enumerate(self.steps):
            print(f"step: {index} : {step}")