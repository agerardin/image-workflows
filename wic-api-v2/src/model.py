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
    class_: str = Field(..., alias='class')   

class SubworkflowFeatureRequirement(ProcessRequirement):
    pass

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
    glob: Optional[str]
    loadContents: Optional[bool]
    outputEval: Optional[str]


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
    type: Optional[str] = "MISSING_TYPE"

WorkflowStepOutput = NewType("WorkflowStepOutput", str)

# TODO CHECK this does not work.
# Revisit and see if we can declared a type
# that serialize to string instead
# This could be useful when adding custom logic.
# @dataclass
# class WorkflowStepOutput(str):
#     pass

class WorkflowStep(BaseModel):
    # NOTE if using BaseModel rather than dataclass,
    # we need to use this approach.
    model_config = ConfigDict(populate_by_name=True)

    id: Id
    run: str
    in_: list[WorkflowStepInput] = Field(..., alias='in')
    out: list[WorkflowStepOutput]
    from_builder: Optional[bool] = False

class Process(BaseModel):
    id: Id

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

class Workflow(Process):
    inputs: list[WorkflowInputParameter]
    outputs: list[WorkflowOutputParameter]
    steps: list[WorkflowStep]
    requirements: Optional[list[ProcessRequirement]] = None
    from_builder: Optional[bool] = False
    # TODO CHECK if we can factor in process
    class_: Optional[str] = Field(..., alias='class')
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


# workflow_file= Path("/Users/antoinegerardin/Documents/projects/polus-pipelines/wic-api-v2/tests/test-data/cwl/workflow5.cwl")
# cwl_wf1 = cwl_parser.load_document_by_uri(workflow_file)
# yaml_wf1 = cwl_parser.save(cwl_wf1)
# wf1 = Workflow(**yaml_wf1)
# print(wf1)
# wf1_out = wf1.dump()
# print(wf1_out)

# subworkflow_file = Path("/Users/antoinegerardin/Documents/projects/polus-pipelines/wic-api-v2/tests/test-data/cwl/subworkflow1.cwl")
# cwl_wf2 = cwl_parser.load_document_by_uri(subworkflow_file)
# yaml_wf2 = cwl_parser.save(cwl_wf2)
# wf2 = Workflow(**yaml_wf2)
# print(wf2)

# class StepBuilder():
#     """Builder for a step object.
    
#     Create a step from a clt.
#     Each inputs/outputs of the clt are instantiated as step in/out.
#     When the final step is returned, 
#     - unset inputs are removed.
#     - outputs which are source of another step or outputSource of 
#     workflow step are removed.
#     """

#     def __init__(self, clt : Process):
#         # TODO REVIEW tentative
#         id = "step_"+ Path(clt.id).stem
#         run = clt.id
#         inputs = [{"id":input.id, "source":"UNSET", "type": input.type} for input in clt.inputs]
#         outputs = [output.id for output in clt.outputs]
#         self.step = WorkflowStep(
#             id = id,
#             run = run,
#             in_ = inputs,
#             out = outputs,
#             from_builder = True
#             )

#     def __call__(self) -> WorkflowStep:
#         return self.step

# class  WorkflowBuilder():
#     """Builder for a workflow object.
    
#     Enable iteratively to create a workflow.
#     """
#     def __init__(self, id: str, *args: Any, **kwds: Any):
#         kwds.setdefault("steps", [])
#         # collect all step inputs create a workflow input for each
#         # collect all step outputs and create a workflow output for each
#         # NOTE for now each output from each step creates an output
#         # TODO make this optional
#         # TODO we could also reduced workflow outputs to only those 
#         # which are not already connected.
#         inputs = []
#         outputs = []
#         for step in kwds.get("steps"):
#             step_inputs = [{"id": id + "/" + step.id + "/" + input.id, "type":input.type} for input in step.in_ if input.source == 'UNSET']
#             inputs = inputs + step_inputs

#             step_types = {}

#             print(f"run {step.run}")
#             cwl_file = cwl_parser.load_document_by_uri(step.run)
#             yaml_cwl = cwl_parser.save(cwl_file)
#             if cwl_file.class_ == "CommandLineTool":
#                 clt = CommandLineTool(**yaml_cwl)
#                 output_types = {output.id:output.type for output in clt.outputs}
#                 step_types[step.id]= output_types

#             #TODO IMPLEMENT same thing for workflow (need to recursive load types)

#             step_outputs = [
#                             {
#                             "id": id + "/" + step.id + "/" + output,
#                             "type": step_types[step.id][output], 
#                             "outputSource": step.id + "/" + output
#                             } for output in step.out
#                             ]
#             outputs = outputs + step_outputs

#         kwds.setdefault("inputs", inputs)
#         kwds.setdefault("outputs", outputs)

#         # NOTE for this to work, we would need to serialize to disk
#         # TODO CHECK if there is a better way to solve this
#         id = (Path() / (id + ".cwl")).resolve().as_uri()
#         kwds.setdefault("id", id)

#         self.workflow = Workflow(**kwds, from_builder=True)

#     def __call__(self) -> Any:
#         workflow = self.workflow
#         # NOTE this is probably a temporary workaround, but 
#         # we need to be able to load the original cwl when creating subworkflows.
#         # TODO IMPLEMENT we could also accept a context object containing models of 
#         # clts and workflows.
#         self.workflow.dump()
#         return self.workflow

#     def step():
#         pass

# print(clt)

# # build a first step
# step_builder = StepBuilder(clt)
# step1 = step_builder()
# print(step1)

# # load a second tool
# clt_file2 = Path("/Users/antoinegerardin/Documents/projects/polus-pipelines/wic-api-v2/tests/test-data/wic/cwl_adapters/uppercase2_wic_compatible2.cwl")
# cwl_clt2 = cwl_parser.load_document_by_uri(clt_file2)
# yaml_clt2 = cwl_parser.save(cwl_clt2)
# clt2 = CommandLineTool(**yaml_clt2)

# # build our second step
# step_builder2 = StepBuilder(clt2)
# step2 = step_builder2()
# print(step2)

# # NOTE that is simulating the linking between 2 steps ios.
# echo_out_message_string = step1.out[0]
# uppercase_in_message = step2.in_[0]
# uppercase_in_message.source = step1.id + "/" + echo_out_message_string

# echo_out_message_string = step1.out[0]
# uppercase_message_in_message = step2.in_[1]
# uppercase_message_in_message.source = step1.id + "/" + echo_out_message_string



# workflow_file= Path("/Users/antoinegerardin/Documents/projects/polus-pipelines/wic-api-v2/tests/test-data/cwl/workflow7.cwl")
# cwl_wf1 = cwl_parser.load_document_by_uri(workflow_file)
# yaml_wf1 = cwl_parser.save(cwl_wf1)
# wf1 = Workflow(**yaml_wf1)
# print(wf1)

# wf2_builder = WorkflowBuilder("wf3", steps=[step1, step2])
# wf3 = wf2_builder()
# print(wf3)

# step_builder3 = StepBuilder(wf3)
# step3 = step_builder3()
# print(step3)



# wf4_builder = WorkflowBuilder("wf4", steps = [step3])
# step4 = wf4_builder()
# print(step4)

