"""Test the workflow builder."""

import pytest
from pathlib import Path

from polus.pipelines.workflows import (
    CommandLineTool, Workflow, StepBuilder, WorkflowBuilder, run_cwl
)


@pytest.mark.parametrize("clts", [["echo_string.cwl", "uppercase2_wic_compatible2.cwl"]])
def test_workflow_builder(test_data_dir: Path, clts: list[str]):
    """Build a basic workflow from steps."""
    steps_input_count = 0
    steps_output_count = 0
    steps = []
    for filename in clts:
        cwl_file = test_data_dir / filename
        clt = CommandLineTool.load(cwl_file)
        step = StepBuilder(clt)()
        steps_input_count += len(step.in_)
        steps_output_count += len(step.out)
        steps.append(step)
    wf_builder = WorkflowBuilder("wf3", steps=steps)
    wf: Workflow = wf_builder()

    input_count = len(wf.inputs)
    assert input_count == steps_input_count, f"workflow should have {steps_input_count} input, got {input_count}." 
    output_count = len(wf.outputs)
    assert output_count == steps_output_count, f"workflow should have {steps_output_count} input, got {output_count}."


@pytest.mark.parametrize("clts", [["echo_string.cwl", "uppercase2_wic_compatible2.cwl"]])
def test_workflow_builder_with_linked_steps(test_data_dir: Path, clts: list[str]):
    """Build a basic workflow from steps and link their ios."""
    steps_input_count = 0
    steps_output_count = 0
    steps = []
    for filename in clts:
        cwl_file = test_data_dir / filename
        clt = CommandLineTool.load(cwl_file)
        step = StepBuilder(clt)()
        steps_input_count += len(step.in_)
        steps_output_count += len(step.out)
        steps.append(step)

    # link steps
    (step1, step2) = steps
    step2.message = step1.message_string
    step2.uppercase_message = step1.message_string

    wf_builder = WorkflowBuilder("wf3", steps=steps)
    wf: Workflow = wf_builder()

    input_count = len(wf.inputs)
    # we have linked 2 inputs from the second step
    # so they should not be part of the final model.
    expected_count = steps_input_count - 2
    assert input_count == expected_count, f"workflow should have {expected_count} input, got {input_count}." 


@pytest.mark.parametrize("clts", [["echo_string.cwl", "uppercase2_wic_compatible2.cwl", "touch_single.cwl"]])
def test_workflow_builder_with_subworkflows(test_data_dir: Path, clts: list[str]):
    """Build and run a workflow containing another workflow and link their ios."""
    steps = []
    for filename in clts:
        cwl_file = test_data_dir / filename
        clt = CommandLineTool.load(cwl_file)
        step_builder = StepBuilder(clt)
        step = step_builder()
        steps.append(step)

    (step1, step2, step3) = steps
    step2.message = step1.message_string
    step2.uppercase_message = step1.message_string

    wf_builder = WorkflowBuilder("wf3", steps=[step1, step2])
    wf: Workflow = wf_builder()
    step_builder = StepBuilder(wf)
    step12 = step_builder()

    # TODO CHECK yep names become quickly unwieldly. See how we can do better.
    step3.touchfiles = step12.wf3___step_uppercase2_wic_compatible2___uppercase_message
    
    wf_builder = WorkflowBuilder("wf4", steps = [step12, step3])
    main_wf = wf_builder()

    step_builder = StepBuilder(main_wf)
    step4 = step_builder()

    step4.wf4___step_wf3___wf3___step_echo_string___message = "test_message"
    config = step4.save_config()

    run_cwl(Path()/f"{main_wf.name}.cwl", config_file=config)
