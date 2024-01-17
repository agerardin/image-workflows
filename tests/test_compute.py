"""Tests the compute package."""

import pytest
from pathlib import Path
import os
import requests

from polus.pipelines.compute.token_service import get_access_token
from polus.pipelines.compute import (
    submit_pipeline
    )
from polus.pipelines import (
    ConfigError, TokenError, ComputeError
)

from polus.pipelines.utils import load_json, save_json

@pytest.mark.skipif("not config.getoption('integration')")
def test_get_access_token() -> None:
    access_token = get_access_token()
    assert isinstance(access_token,str)


@pytest.mark.skipif("not config.getoption('integration')")
def test_submit_pipeline(compute_pipeline_file: Path) -> None:
    compute_url = os.environ.get("COMPUTE_URL")
    print(compute_url)
    resp = submit_pipeline(compute_pipeline_file)
    assert (resp.status_code == 201)


def test_invalid_token(compute_pipeline_file: Path) -> None:
    with pytest.raises(TokenError):
        os.environ["ACCESS_TOKEN"] = "BAD_TOKEN"
        resp = submit_pipeline(compute_pipeline_file)


def test_missing_token(compute_pipeline_file: Path) -> None:
    with pytest.raises(ConfigError):
        del os.environ["COMPUTE_URL"]
        resp = submit_pipeline(compute_pipeline_file)

def test_bad_url(compute_pipeline_file: Path) -> None:
    with pytest.raises(requests.exceptions.ConnectionError):
        os.environ["COMPUTE_URL"] = "https://BAD_URL"
        resp = submit_pipeline(compute_pipeline_file)

def test_bad_compute_spec(compute_pipeline_file: Path) -> None:
        with pytest.raises(ComputeError):
            json = load_json(compute_pipeline_file)
            json["driver"] = "DRIVER_NOT_EXIST"
            tmp_spec = Path("bad_compute_spec.json")
            save_json(json, tmp_spec)
            submit_pipeline(tmp_spec)
        os.remove(tmp_spec)
