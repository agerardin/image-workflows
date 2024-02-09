from typing import Union
from pydantic import BaseModel, ConfigDict, Field
import cwl_utils.parser as cwl_parser
from pathlib import Path
from yaml import safe_load
from pydantic.dataclasses import dataclass
from typing import NewType, Optional, Any
from rich import print


Id = NewType("Id", str)

@dataclass
class Process():
    id: str

@dataclass
class InputBinding:
    pass

# TODO CHANGE for now stick to cwl_parser
# but should be CLTInputBinding
@dataclass
class CommandLineBinding(InputBinding):
    position: Optional[int] = None

# TODO CHANGE for now stick to cwl_parser
# but should be CLTOutputBinding
@dataclass
class CommandOutputBinding:
    glob: Optional[str]
    loadContents: Optional[bool]
    outputEval: Optional[str]

@dataclass
class Parameter:
    id: Id
    type: str

@dataclass
class InputParameter(Parameter):
    pass

class OutputParameter(Parameter):
    pass

@dataclass
class WorkflowInputParameter(InputParameter):
    pass
@dataclass
class WorkflowOutputParameter(OutputParameter):
    outputSource: str

@dataclass
class CommandInputParameter(InputParameter):
    inputBinding: Optional[CommandLineBinding]

@dataclass
class CommandOutputParameter(OutputParameter):
    outputBinding: Optional[CommandOutputBinding]


@dataclass
class WorkflowStepInput():
    id: str
    source: str

WorkflowStepOutput = NewType("WorkflowStepOutput", str)

# TODO CHECK this does not work.
# Revisit and see if we can declared a type
# that serialize to string instead
# This could be useful when adding custom logic.
# @dataclass
# class WorkflowStepOutput(str):
#     pass

class WorkflowStep(BaseModel):
    id: Id
    run: str
    out: list[WorkflowStepOutput]
    in_: list[WorkflowStepInput] = Field(..., alias='in')
    # model_config = ConfigDict(populate_by_name=True)

@dataclass
class Workflow(Process):
    inputs: list[WorkflowInputParameter]
    outputs: list[WorkflowOutputParameter]
    steps: list[WorkflowStep]
    #inputs: dict[Id, WorkflowInputParameter]
    #outputs: dict[Id, WorkflowOutputParameter]

@dataclass
class CommandLineTool(Process):
   id : Id
   doc: str
   label: str
   baseCommand: str
   inputs: list[CommandInputParameter]
   outputs: list[CommandOutputParameter]
   # TODO maybe have transformation to store dict
   # but only if we don't need ordering
   # inputs: dict[Id, CommandInputParameter]
   # outputs: dict[Id, CommandOutputParameter]
   stdout: Optional[str]

class ExpressionTool:
    pass

class DockerRequirement:
    pass 

class Operation:
    pass



class ProcessRequirement:
    pass

class SoftwareRequirement:
    pass


cwl_file = Path("/Users/antoinegerardin/Documents/projects/polus-pipelines/wic-api-v2/tests/test-data/cwl/echo_string.cwl")

with cwl_file.open("r", encoding="utf-8") as file:
    raw_clt = safe_load(file)

# NOTE we use the cwl_parser to standardize the representation
cwl_clt = cwl_parser.load_document_by_uri(cwl_file)
yaml_clt = cwl_parser.save(cwl_clt)


clt = CommandLineTool(**yaml_clt)
print(clt)

workflow_file= Path("/Users/antoinegerardin/Documents/projects/polus-pipelines/wic-api-v2/tests/test-data/cwl/workflow5.cwl")
cwl_wf1 = cwl_parser.load_document_by_uri(workflow_file)
yaml_wf1 = cwl_parser.save(cwl_wf1)
wf1 = Workflow(**yaml_wf1)
print(wf1)