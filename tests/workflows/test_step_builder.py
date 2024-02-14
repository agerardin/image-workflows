import pytest

from pathlib import Path
import logging
from rich import print

from polus.pipelines.workflows import (
    CommandLineTool, Workflow, StepBuilder
)

logger = logging.getLogger()

@pytest.mark.parametrize("filename", ["echo_string.cwl"])
def test_step_builder(test_data_dir: Path, filename):
    cwl_file = test_data_dir / filename
    clt = CommandLineTool.load(cwl_file)
    print(clt)
    step_builder = StepBuilder(clt)
    step = step_builder()
    print(step)
