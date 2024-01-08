import pytest
import yaml
from pathlib import Path
from pydantic import ValidationError
from polus.pipelines.models import Pipeline

@pytest.fixture
def path():
    # print(Path("config/process/BBBC/BBBC001_process.yaml").absolute())
    return Path("config/process/BBBC/BBBC001_process.yaml").absolute()

@pytest.fixture
def pipeline_spec(path: str):
    with open(path, 'r') as file:
        spec = yaml.safe_load(file)
        yield spec

def test_pipeline_model(pipeline_spec : Path):
    print(pipeline_spec)
    try: 
        pipeline = Pipeline(**pipeline_spec)
    except ValidationError as e:
        print(e)
        raise e
