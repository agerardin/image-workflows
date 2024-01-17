"""Test build package."""

from pathlib import Path

import pytest
from polus.pipelines.build import (
    build_compute_pipeline,
    build_workflow,
    save_compute_pipeline
    )


def test_build_workflow(spec_path: Path) -> None:
    """Test that we can build a cwl workflow for a spec file."""
    workflow = build_workflow(spec_path)
    step_count = 5
    assert (
        len(workflow.steps) == step_count
    ), f"pipelines spec at : {spec_path} should have {step_count} steps."


def test_generate_compute_workflow(spec_path: Path) -> None:
    """Test we can build a valid cwl pipeline."""
    workflow = build_workflow(spec_path)
    output_path = save_compute_pipeline(workflow)
    assert output_path.is_file()


def test_build_pipeline(spec_path: Path) -> None:
    """Test we can build a valid cwl pipeline."""
    output_path = build_compute_pipeline(spec_path)
    assert output_path.is_file()