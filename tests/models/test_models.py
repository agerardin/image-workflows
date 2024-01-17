"""Test for the models package."""


from pathlib import Path

import pytest
import yaml
from polus.pipelines.models import Pipeline
from pydantic import ValidationError


@pytest.fixture()
def path() -> Path:
    """Path fixture."""
    return Path("config/process/BBBC/BBBC001_process.yaml").resolve()


@pytest.fixture()
def pipeline_spec(path: Path) -> object:
    """Spec file fixture."""
    with Path.open(path) as file:
        spec = yaml.safe_load(file)
        yield spec


def test_pipeline_model(pipeline_spec: Path) -> None:
    """Test we can marshall the pipeline spec into our pydantic model."""
    try:
        Pipeline(**pipeline_spec)
    except ValidationError as e:
        raise e
