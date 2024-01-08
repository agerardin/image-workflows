"""Test api."""

from pathlib import Path

import pytest
from polus.pipelines import build_pipeline
from polus.pipelines import build_workflow
from polus.pipelines import generate_compute_workflow


@pytest.fixture()
def path() -> Path:
    """Path fixture."""
    return Path("config/process/BBBC/BBBC001_process.yaml").absolute()


def test_build_workflow(path: Path) -> None:
    """Test that we can build a cwl workflow for a spec file."""
    workflow = build_workflow(path)
    step_count = 5
    assert (
        len(workflow.steps) == step_count
    ), f"pipelines spec at : {path} should have {step_count} steps."


def test_generate_compute_worklfow(path: Path) -> None:
    """Test we can build a valid cwl pipeline."""
    workflow = build_workflow(path)
    output_path = generate_compute_workflow(workflow)
    assert output_path.is_file()


def test_build_pipeline(path: Path) -> None:
    """Test we can build a valid cwl pipeline."""
    output_path = build_pipeline(path)
    assert output_path.is_file()
