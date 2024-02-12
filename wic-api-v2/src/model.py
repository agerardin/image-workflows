from typing import Union
from pydantic import (
    BaseModel, ConfigDict, Field, ValidationError,
    computed_field
)
import cwl_utils.parser as cwl_parser
from pathlib import Path
from yaml import safe_load, dump
import yaml
from pydantic.dataclasses import dataclass
from typing import NewType, Optional, Any
from rich import print
from urllib.parse import unquote, urlparse
# TODO update to v2 if we want to go this route
# RootModel us used to serialize dataclasses
# from pydantic import RootModel

def validate_file(file_path):
    file_path = file_path.resolve()
    if not file_path.exists:
        raise FileNotFoundError
    if not file_path.is_file():
        raise NotAFileError()
    return file_path


class NotAFileError(Exception):
    pass


Id = NewType("Id", str)

class ProcessRequirement(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

class SubworkflowFeatureRequirement(ProcessRequirement):
    class_: Optional[str] = Field("SubworkflowFeatureRequirement", alias='class')

class SoftwareRequirement(ProcessRequirement):
    pass

class DockerRequirement(ProcessRequirement):
    pass 

class InputBinding(BaseModel):
    pass

# TODO CHANGE for now stick to cwl_parser
# but should be CLTInputBinding
class CommandLineBinding(InputBinding, extra='ignore'):
    position: Optional[int] = None

# TODO CHANGE for now stick to cwl_parser
# but should be CLTOutputBinding

class CommandOutputBinding(BaseModel):
    glob: Optional[str] = None
    loadContents: Optional[bool] = None
    outputEval: Optional[str] = None


class Parameter(BaseModel):
    id: Id
    type: str

class InputParameter(Parameter):
    pass

class OutputParameter(Parameter):
    pass


class WorkflowInputParameter(InputParameter):
    pass


class WorkflowOutputParameter(OutputParameter):
    outputSource: str

class CommandInputParameter(InputParameter):
    inputBinding: Optional[CommandLineBinding] = None


class CommandOutputParameter(OutputParameter):
    outputBinding: Optional[CommandOutputBinding] = None

class WorkflowStepInput(BaseModel):
    id: str
    source: str
    # TODO CHECK. WorkflowStepInput does not have type.
    # However, when building by hand, we will rely on this to check
    # the link is valid, without having to go back to the clt definition.
    type: Optional[str] = Field("MISSING_TYPE", exclude=True)

WorkflowStepOutput = NewType("WorkflowStepOutput", str)

# TODO CHECK this does not work.
# Revisit and see if we can declared a type
# that serialize to string instead
# This could be useful when adding custom logic.
# @dataclass
# class WorkflowStepOutput(str):
#     pass

class WorkflowStep(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: Id
    run: str
    in_: list[WorkflowStepInput] = Field(..., alias='in')
    out: list[WorkflowStepOutput]
    from_builder: Optional[bool] = Field(False, exclude=True)

    # TODO CHECK we could also keep track of a dictionary of clt
    # names for checking WorkflowStepInput type. Let's see what
    # makes more sense.

class Process(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    id: Id

    # TODO can class be declared there and overidden in subclasses?

    @computed_field
    @property
    def name(self) -> str:
        # TODO CHECK this works for any allowable CLT
        name = Path(self.id).stem
        return name
    
    def save(self, path = Path()) -> Path:
        """
        Create a cwl file.
        Process computed name is ignored.

        Args:
            - path : the directories in which in to create the file.
        """
        path = path.resolve()
        if not path.exists():
            raise FileNotFoundError()
        if not path.is_dir():
            # TODO create exception for this?
            # TODO fallback (like checking parent and using it?)
            raise Exception(f"{path} is not a directory.")

        file_path = path / (self.name + ".cwl")
        serialized_process = self.model_dump(by_alias=True, exclude={'name'})
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(dump(serialized_process))
            return file_path 
        
    # TODO CHECK can we have equivalent of virtual methods in python?
    # load() should be defined by subclass but declared here.

class Workflow(Process):
    inputs: list[WorkflowInputParameter]
    outputs: list[WorkflowOutputParameter]
    steps: list[WorkflowStep]
    requirements: Optional[list[dict[str, object]]] = []
    from_builder: Optional[bool] = Field(False, exclude=True)
    # TODO CHECK if we can factor in process
    class_: Optional[str] = Field(alias='class', default='Workflow')
    cwlVersion: str = "v1.2"
    # TODO maybe have transformation to store dict
    #inputs: dict[Id, WorkflowInputParameter]
    #outputs: dict[Id, WorkflowOutputParameter]

    @classmethod
    def load(cls, clt_file: Path) -> 'CommandLineTool':
        """Load a Workflow from a cwl workflow file.
        
        We use the reference cwl parser to get a standardized description.
        """
        clt_file = validate_file(clt_file)
        cwl_clt = cwl_parser.load_document_by_uri(clt_file)
        # TODO CHECK save rewrite ids and runs ref.
        # Make sure this is not an issue.
        # In particular rewrite runs can be an issue if not managed properly
        # (could have clashing definitions).
        yaml_clt = cwl_parser.save(cwl_clt)
        return cls(**yaml_clt) 

class CommandLineTool(Process):
    model_config = ConfigDict(extra='ignore')
    baseCommand: str
    inputs: list[CommandInputParameter]
    outputs: list[CommandOutputParameter]
    # TODO maybe have transformation to store dict
    # but only if we don't need ordering
    #inputs: dict[Id, CommandInputParameter]
    #outputs: dict[Id, CommandOutputParameter]
    class_: Optional[str] = Field(..., alias='class') 
    cwlVersion: Optional[str] = "v1.2"
    stdout: Optional[str] = None
    doc: Optional[str] = ""
    label: Optional[str] = ""

    @classmethod
    def load(cls, clt_file: Path) -> 'CommandLineTool':
        """Load a CLT from a cwl clt file.
        
        We use the reference cwl parser to get a standardized description.
        """
        clt_file = validate_file(clt_file)
        cwl_clt = cwl_parser.load_document_by_uri(clt_file)
        yaml_clt = cwl_parser.save(cwl_clt)
        return cls(**yaml_clt) 

class ExpressionTool:
    pass

class Operation:
    pass

class StepBuilder():
    """Create a workflow step.
    
    Create a WorkflowStep from a CommandLineTool.
    For each input/output of the clt, a corresponding step in/out is created.
    """

    def __init__(self, clt : Process):
        # Generate a step id from the clt name
        id = "step_"+ clt.name
        run = clt.id
        # TODO change. For now set source to "UNSET"
        inputs = [{"id":input.id, "source":"UNSET", "type": input.type}
                  for input in clt.inputs]
        outputs = [output.id for output in clt.outputs]
        self.step = WorkflowStep(
            id = id,
            run = run,
            in_ = inputs,
            out = outputs,
            from_builder = True
            )

    def __call__(self) -> WorkflowStep:
        return self.step

class  WorkflowBuilder():
    """Builder for a workflow object.
    
    Enable iteratively to create a workflow.
    """
    def __init__(self, id: str, *args: Any, **kwds: Any):
        kwds.setdefault("steps", [])
        # Collect all step inputs and create a workflow input for each
        # Collect all step outputs and create a workflow output for each
        # NOTE For now each output from each step creates an output.
        # TODO Make this optional.
        # TODO We could also reduced workflow outputs to only those 
        # which are not already connected.
        # TODO Similarly we could have an option to hide/rename steps the list 
        # of workflow inputs.
        def generate_workflow_io_id(worklflow_id : str, step_id: str, io_id: str):
            """generate id for workflow ios. Note that ('/') are forbidden."""
            return worklflow_id + "___" + step_id + "___" + io_id

        workflow_inputs = []
        worklfow_inputs = []
        for step in kwds.get("steps"):
            for input in step.in_:
                if input.source == 'UNSET':
                    workflow_input_id = generate_workflow_io_id(id, step.id, input.id)
                    workflow_input = {"id": workflow_input_id, "type":input.type}
                    input.source = workflow_input_id
                    workflow_inputs.append(workflow_input)

            # TODO That is where a context of loaded CLTs could be helpful.
            # So we don't keep reloading the same models.

            # Collect types of each CLT inputs referenced.
            # TODO probably should do it anyhow because we could parse
            # non generated steps.
            # Check that generated steps have correct input types?
            step_types = {}
            cwl_file = cwl_parser.load_document_by_uri(step.run)
            yaml_cwl = cwl_parser.save(cwl_file)
            if cwl_file.class_ == "CommandLineTool":
                clt = CommandLineTool(**yaml_cwl)
                output_types = {output.id:output.type for output in clt.outputs}
                step_types[step.id] = output_types
            elif cwl_file.class_ == "Workflow":
                workflow = Workflow(**yaml_cwl)
                output_types = {output.id:output.type for output in workflow.outputs}
                step_types[step.id] = output_types
                kwds.setdefault("requirements", [{"class": "SubworkflowFeatureRequirement"}])
            else:
                raise Exception(f"Invalid Cwl Class : {cwl_file.class_}")

            step_outputs = [
                            {
                            "id": generate_workflow_io_id(id, step.id, output),
                            "type": step_types[step.id][output], 
                            "outputSource": step.id + "/" + output
                            } for output in step.out
                            ]
            # For now, every step output becomes a workflow output.
            worklfow_inputs = worklfow_inputs + step_outputs

        kwds.setdefault("inputs", workflow_inputs)
        kwds.setdefault("outputs", worklfow_inputs)

        # NOTE for this to work, we would need to serialize to disk
        # TODO CHECK if there is a better way to solve this
        id = (Path() / (id + ".cwl")).resolve().as_uri()
        kwds.setdefault("id", id)

        self.workflow = Workflow(**kwds, from_builder=True)

    def __call__(self) -> Any:
        workflow = self.workflow
        # NOTE this is probably a temporary workaround, but 
        # we need to be able to load the original cwl when creating subworkflows.
        # TODO IMPLEMENT we could also accept a context object containing models of 
        # clts and workflows.
        self.workflow.save()
        return self.workflow

    def step():
        pass

