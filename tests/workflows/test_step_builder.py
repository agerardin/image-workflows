"""Test we can build a step from a cwl clt file."""

import pytest
from pathlib import Path

from polus.pipelines.workflows import (
    CommandLineTool, StepBuilder
)


@pytest.mark.parametrize("filename", ["echo_string.cwl"])
def test_step_builder(test_data_dir: Path, filename:str):
    """Test we can build a step from a cwl clt file."""
    cwl_file = test_data_dir / filename
    clt = CommandLineTool.load(cwl_file)
    step_builder = StepBuilder(clt)
    step = step_builder()
