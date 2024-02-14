import pytest

from pathlib import Path
import logging
from rich import print

from polus.pipelines.workflows import (
    CommandLineTool, Workflow
)

logger = logging.getLogger()

@pytest.mark.parametrize("filename", ["echo_string.cwl"])
def test_load_clt(test_data_dir: Path, filename):
    cwl_file = test_data_dir / filename
    clt = CommandLineTool.load(cwl_file)
    print(clt)

@pytest.mark.parametrize("filename", ["workflow5.cwl","workflow7.cwl"])
def test_load_workflow(test_data_dir: Path, tmp_dir: Path, filename):
    cwl_file = test_data_dir / filename
    wf1 = Workflow.load(cwl_file)
    print(wf1)

@pytest.mark.parametrize("filename", ["subworkflow1.cwl"])
def test_load_subworkflow(test_data_dir: Path, tmp_dir: Path, filename):
    cwl_file = test_data_dir / filename
    wf2 = Workflow.load(cwl_file)
    print(wf2)

# TODO So cwlparser does not check the referenced clts,
# It justs check the definition is valid at the first level.
# So if we wanted to more validation, we would need to recursively pull all references.
# NOTE we could provide a Context object to collect definition
# instead of parsing clts over and over.
@pytest.mark.skip(reason="not implemented")
def test_recursive_load():
    pass



