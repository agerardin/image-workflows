import pytest

from pathlib import Path
import logging
from rich import print

from polus.pipelines.workflows import (
    CommandLineTool, Workflow, StepBuilder, WorkflowBuilder
)

logger = logging.getLogger()

@pytest.mark.parametrize("clts", [["echo_string.cwl", "uppercase2_wic_compatible2.cwl"]])
def test_workflow_builder_with_linked_steps(test_data_dir: Path, clts: list[str]):
    steps = []
    for filename in clts:
        cwl_file = test_data_dir / filename
        clt = CommandLineTool.load(cwl_file)
        print(clt)
        step_builder = StepBuilder(clt)
        step = step_builder()
        print(step)
        steps.append(step)

    wf_builder = WorkflowBuilder("wf3", steps=steps)
    wf: Workflow = wf_builder()
    print(wf)

    input_count = len(wf.inputs)
    expected_count = 2
    assert input_count == expected_count, f"workflow should have {expected_count} input, got {input_count}." 


@pytest.mark.parametrize("clts", [["echo_string.cwl", "uppercase2_wic_compatible2.cwl"]])
def test_workflow_builder_with_linked_steps(test_data_dir: Path, clts: list[str]):
    steps = []
    for filename in clts:
        cwl_file = test_data_dir / filename
        clt = CommandLineTool.load(cwl_file)
        print(clt)
        step_builder = StepBuilder(clt)
        step = step_builder()
        print(step)
        steps.append(step)

    (step1, step2) = steps
    step2.message = step1.message_string
    step2.uppercase_message = step1.message_string

    wf_builder = WorkflowBuilder("wf3", steps=steps)
    wf: Workflow = wf_builder()
    print(wf)

    input_count = len(wf.inputs)
    expected_count = 1
    assert input_count == expected_count, f"workflow should have {expected_count} input, got {input_count}." 