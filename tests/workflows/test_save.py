import pytest

from pathlib import Path
import logging

from polus.pipelines.workflows import (
    CommandLineTool, Workflow
)

logger = logging.getLogger()

@pytest.mark.parametrize("filename", ["echo_string.cwl"])
def test_save_clt(test_data_dir: Path, filename):
    cwl_file = test_data_dir / filename
    new_model = CommandLineTool.load(cwl_file)
    new_model.save()

@pytest.mark.parametrize("filename", ["workflow5.cwl"])
def test_save_workflow(test_data_dir: Path, filename):
    cwl_file = test_data_dir / filename
    wf1 = Workflow.load(cwl_file)
    wf1.save()

@pytest.mark.parametrize("filename", ["subworkflow1.cwl"])
def test_save_subworkflow(test_data_dir: Path, filename):
    cwl_file = test_data_dir / filename
    wf2 = Workflow.load(cwl_file)
    wf2.save()

# TODO 
@pytest.mark.skip(reason="not implemented")
def test_recursive_save():
    pass