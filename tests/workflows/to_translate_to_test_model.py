import yaml
from pathlib import Path
import cwl_utils.parser as cwl_parser
from polus.pipelines.workflows import (
    CommandLineTool, Workflow,
    StepBuilder, WorkflowBuilder
)
import logging
from rich import print
import filecmp
import tempfile
import shutil

logger = logging.getLogger()

workflow_file= Path("tests/workflow5.cwl")
wf1 = Workflow.load(workflow_file)
print(wf1)

subworkflow_file = Path("tests/subworkflow1.cwl")
wf2 = Workflow.load(subworkflow_file)
wf2.save()
print(wf2)

# TODO So cwlparser does not check the referenced clts,
# It justs check the definition is valid at the first level.
# So we will need to pull all references first.
# For that, provide a Context object so we parse clts over and over.


# load a clt
echo_file = Path("tests/echo_string.cwl")
echo = CommandLineTool.load(echo_file)
print(echo)

# build a first step
step_builder = StepBuilder(echo)
step1 = step_builder()
print(step1)

step1.message = "ok"

print(step1)

# load a second clt
uppercase_file = Path("tests/uppercase2_wic_compatible2.cwl")
uppercase = CommandLineTool.load(uppercase_file)
print(uppercase)

# build our second step
step_builder2 = StepBuilder(uppercase)
step2 = step_builder2()
print(step2)

step2.message = step1.message_string
step2.uppercase_message = step1.message_string

print(step1)
print(step2)

wf3_builder = WorkflowBuilder("wf3", steps=[step1, step2])
wf3 = wf3_builder()
print(wf3)

workflow_file2= Path("tests/workflow7.cwl")
wf2 = Workflow.load(workflow_file2)
wf2.save()
print(wf2)

step_builder3 = StepBuilder(wf3)
step3 = step_builder3()
print(step3)

touch_file = Path("tests/touch_single.cwl")
touch = CommandLineTool.load(touch_file)
print(touch)
step_builder_touch = StepBuilder(touch)
touch_step = step_builder_touch()

touch_step.touchfiles = step3.wf3___step_uppercase2_wic_compatible2___uppercase_message

wf4_builder = WorkflowBuilder("wf4", steps = [step3, touch_step])


wf4 = wf4_builder()

step_builder4 = StepBuilder(wf4)
step4 = step_builder4()

print("--------------")

print(wf4)

step4.wf4___step_wf3___wf3___step_echo_string___message = "ok"
step4.save_config()







