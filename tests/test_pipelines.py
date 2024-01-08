from polus.pipelines import build_workflow, build_pipeline
from pathlib import Path
import pytest

@pytest.fixture
def path():
    return Path("config/process/BBBC/BBBC001_process.yaml").absolute()

def test_build_workflow(path : Path):
    workflow = build_workflow(path)
    step_count = 5
    assert len(workflow.steps) == step_count, f"pipelines spec at : {path} should have {step_count} steps." # noqa: F401

def test_build_pipeline(path: Path):
    output_path = build_pipeline(path)
    assert output_path.is_file()