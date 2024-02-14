import yaml
from pathlib import Path
import cwl_utils.parser as cwl_parser
from model import (
    CommandLineTool, Workflow,
    StepBuilder, WorkflowBuilder
)
from rich import print

# conditional_workflow_file= Path("tests/conditional-workflow.cwl")
# scatter_wf = Workflow.load(conditional_workflow_file)
# scatter_wf.save()
# print(scatter_wf)

# load a clt
echo_uppercase_wf_file = Path("tests/workflow3.cwl")
echo_uppercase_wf = Workflow.load(echo_uppercase_wf_file)
# print(echo)
step_builder = StepBuilder(echo_uppercase_wf)
step1 = step_builder()
# print(step1)

touch_file = Path("tests/touch_single.cwl")
touch = CommandLineTool.load(touch_file)
step_builder = StepBuilder(touch,
                           when="$(inputs.should_execute < 1)",
                           when_input_names=["should_execute"],
                           add_inputs=[{"id": "should_execute",
                                        "type": "string"
                                        }])
step2 = step_builder()
print(step2)

wf3_builder = WorkflowBuilder("conditional_workflow_generated.cwl", steps=[step1, step2])
wf3 = wf3_builder()
print(wf3)
