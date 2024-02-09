from typing import Union
from pydantic import BaseModel, ConfigDict, Field
import cwl_utils.parser as cwl_parser
from pathlib import Path
from yaml import safe_load
from pydantic.dataclasses import dataclass
from typing import NewType, Optional, Any
from rich import print


Id = NewType("Id", str)

class ProcessRequirement(BaseModel):
    class_: str = Field(..., alias='class')   

@dataclass
class SubworkflowFeatureRequirement(ProcessRequirement):
    pass

class SoftwareRequirement:
    pass


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
    inputBinding: Optional[CommandLineBinding] = None

@dataclass
class CommandOutputParameter(OutputParameter):
    outputBinding: Optional[CommandOutputBinding] = None


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
    # NOTE if using BaseModel rather than dataclass,
    # we need to use this approach.
    class Config:
        allow_population_by_field_name = True

    id: Id
    run: str
    in_: list[WorkflowStepInput] = Field(..., alias='in')
    out: list[WorkflowStepOutput]
    from_builder: Optional[bool] = False

@dataclass
class Workflow(Process):
    inputs: list[WorkflowInputParameter]
    outputs: list[WorkflowOutputParameter]
    steps: list[WorkflowStep]
    requirements: Optional[list[ProcessRequirement]] = None
    from_builder: Optional[bool] = False
    class_: str = 'Workflow'
    # TODO maybe have transformation to store dict
    #inputs: dict[Id, WorkflowInputParameter]
    #outputs: dict[Id, WorkflowOutputParameter]

@dataclass
class CommandLineTool(Process):
   id : Id
   baseCommand: str
   inputs: list[CommandInputParameter]
   outputs: list[CommandOutputParameter]
   # TODO maybe have transformation to store dict
   # but only if we don't need ordering
   # inputs: dict[Id, CommandInputParameter]
   # outputs: dict[Id, CommandOutputParameter]
   class_: str = 'CommandLineTool'
   stdout: Optional[str] = None
   doc: Optional[str] = ""
   label: Optional[str] = ""

class ExpressionTool:
    pass

class DockerRequirement:
    pass 

class Operation:
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

subworkflow_file = Path("/Users/antoinegerardin/Documents/projects/polus-pipelines/wic-api-v2/tests/test-data/cwl/subworkflow1.cwl")
cwl_wf2 = cwl_parser.load_document_by_uri(subworkflow_file)
yaml_wf2 = cwl_parser.save(cwl_wf2)
wf2 = Workflow(**yaml_wf2)
print(wf2)

class StepBuilder():
    """Builder for a step object.
    
    Create a step from a clt.
    Each inputs/outputs of the clt are instantiated as step in/out.
    When the final step is returned, 
    - unset inputs are removed.
    - outputs which are source of another step or outputSource of 
    workflow step are removed.
    """

    def __init__(self, clt : Process):
        # TODO REVIEW tentative
        id = "step_"+ Path(clt.id).stem
        run = clt.id
        inputs = [{"id":input.id, "source":"UNSET"} for input in clt.inputs]
        outputs = [output.id for output in clt.outputs]
        self.step = WorkflowStep(id=id,run=run,in_=inputs,out=outputs, from_builder=True)

    def __call__(self) -> WorkflowStep:
        return self.step

class WorkflowBuilder():
    """Builder for a workflow object.
    
    Enable iteratively to create a workflow.
    """
    def __init__(self, id: str, *args: Any, **kwds: Any):
        kwds.setdefault("steps", [])
        # collect all step inputs create a workflow input for each
        # collect all step outputs and create a workflow output for each
        # NOTE for now each output from each step creates an output
        # TODO make this optional
        # TODO we could also reduced workflow outputs to only those 
        # which are not already connected.
        inputs = []
        outputs = []
        for step in kwds.get("steps"):
            step_inputs = [{"id": id + "/" + step.id + "/" + input.id, "type":"TYPE_MISSING"} for input in step.in_ if input.source is 'UNSET']
            inputs = inputs + step_inputs
            step_outputs = [{"id": id + "/" + step.id + "/" + output, "type": "TYPE_MISSING", "outputSource": step.id + "/" + output} for output in step.out]
            outputs = outputs + step_outputs

        kwds.setdefault("inputs", inputs)
        kwds.setdefault("outputs", outputs)

        self.workflow = Workflow(id,*args,**kwds, from_builder=True)

    def __call__(self) -> Any:
        return self.workflow

    def step():
        pass

print(clt)

# build a first step
step_builder = StepBuilder(clt)
step1 = step_builder()
print(step1)

# load a second tool
clt_file2 = Path("/Users/antoinegerardin/Documents/projects/polus-pipelines/wic-api-v2/tests/test-data/wic/cwl_adapters/uppercase2_wic_compatible2.cwl")
cwl_clt2 = cwl_parser.load_document_by_uri(clt_file2)
yaml_clt2 = cwl_parser.save(cwl_clt2)
clt2 = CommandLineTool(**yaml_clt2)

# build our second step
step_builder2 = StepBuilder(clt2)
step2 = step_builder2()
print(step2)

# NOTE that is simulating the linking between 2 steps ios.
echo_out_message_string = step1.out[0]
uppercase_in_message = step2.in_[0]
uppercase_in_message.source = step1.id + "/" + echo_out_message_string

echo_out_message_string = step1.out[0]
uppercase_message_in_message = step2.in_[1]
uppercase_message_in_message.source = step1.id + "/" + echo_out_message_string



workflow_file= Path("/Users/antoinegerardin/Documents/projects/polus-pipelines/wic-api-v2/tests/test-data/cwl/workflow7.cwl")
cwl_wf1 = cwl_parser.load_document_by_uri(workflow_file)
yaml_wf1 = cwl_parser.save(cwl_wf1)
wf1 = Workflow(**yaml_wf1)
print(wf1)

wf2_builder = WorkflowBuilder("wf3", steps=[step1, step2])
wf3 = wf2_builder()
print(wf3)

# step_builder3 = StepBuilder(wf3)
# step3 = step_builder3()
# print(step3)

# wf4_builder = WorkflowBuilder("wf4", steps = [step3, step2])
# step4 = wf4_builder()
# print(step4)



