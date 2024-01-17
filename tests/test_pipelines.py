"""Test api."""

from pathlib import Path
import pytest

from polus.pipelines import (
    build_compute_pipeline,
    build_workflow,
    save_compute_pipeline,
    submit_pipeline
    )


def test_build_api(spec_path: Path) -> None:
    """Test that all build api methods are available at the top package level."""
    build_compute_pipeline(spec_path)
    workflow = build_workflow(spec_path)
    save_compute_pipeline(workflow)


@pytest.mark.skipif("not config.getoption('integration')")
def test_compute_api(compute_pipeline_file: Path) -> None:
    """Test that all compute methods are available at the top package level."""
    submit_pipeline(compute_pipeline_file)
