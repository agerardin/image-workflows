"""Test api."""

from pathlib import Path

import pytest
from polus.pipelines import (
    build_compute_pipeline,
    build_workflow,
    save_compute_pipeline
    )


@pytest.fixture()
def path() -> Path:
    """Path fixture."""
    return Path("config/process/BBBC/BBBC001_process.yaml").resolve()


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
    output_path = save_compute_pipeline(workflow)
    assert output_path.is_file()


def test_build_pipeline(path: Path) -> None:
    """Test we can build a valid cwl pipeline."""
    output_path = build_compute_pipeline(path)
    assert output_path.is_file()
