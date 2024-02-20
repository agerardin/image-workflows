import pytest

from pathlib import Path
import logging
from rich import print

from polus.pipelines.workflows import (
    CommandLineTool, Workflow, StepBuilder, WorkflowBuilder, run_cwl
)

def test_workflow_builder():
    test_data_dir = Path() / "tests" / "workflows" / "test_data"
    clts = ["echo_string.cwl", "uppercase2_wic_compatible2.cwl"]

    steps = []
    for filename in clts:
        cwl_file = test_data_dir / filename
        clt = CommandLineTool.load(cwl_file)
        step_builder = StepBuilder(clt)
        step = step_builder()
        steps.append(step)

    wf_builder = WorkflowBuilder("wf_test_builder", steps=steps)
    wf: Workflow = wf_builder()
    # wf_file = wf.save()

    # run_cwl(wf_file)

test_workflow_builder()