import yaml
from pathlib import Path
import cwl_utils.parser as cwl_parser
from model import (
    CommandLineTool, Workflow,
    StepBuilder, WorkflowBuilder
)
import logging
from rich import print
import filecmp
import tempfile
import shutil

scatter_workflow_file= Path("tests/scatter-workflow2.cwl")
scatter_wf = Workflow.load(scatter_workflow_file)
scatter_wf.save()
# print(scatter_wf)

# load a clt
echo_file = Path("tests/echo_string.cwl")
echo = CommandLineTool.load(echo_file)
# print(echo)

scattered_inputs = [input.id for input in echo.inputs]

print(f"scattered inputs: {scattered_inputs}")

# build a first step
step_builder = StepBuilder(echo)
step1 = step_builder()
print(step1)


# build a scatter step
step_builder = StepBuilder(echo, scatter=scattered_inputs)
step1 = step_builder()
print(step1)

# load a second clt
uppercase_file = Path("tests/uppercase2_wic_compatible3.cwl")
uppercase = CommandLineTool.load(uppercase_file)
print(uppercase)

scattered_inputs = [input.id for input in uppercase.inputs]


# build our second step
step_builder2 = StepBuilder(uppercase, scatter=scattered_inputs)
step2 = step_builder2()

print(step2)

step2.message = step1.message_string
# TODO UGLY MESSAGE WHEN THIS ATTRIBUTE IS NOT PRESENT!
# step2.uppercase_message = step1.message_string

print("----------")
print(step1)
print("----------")
print(step2)

wf3_builder = WorkflowBuilder("wf3_scatter", steps=[step1, step2])
wf3 = wf3_builder()
print(wf3)


