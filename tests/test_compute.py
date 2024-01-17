"""Tests the compute package."""

import pytest
from pathlib import Path
from requests import Response

from polus.pipelines.compute.token_service import get_access_token
from polus.pipelines.compute import submit_pipeline


@pytest.mark.skipif("not config.getoption('integration')")
def test_get_access_token() -> None:
    access_token = get_access_token()
    assert isinstance(access_token,str)


@pytest.mark.skipif("not config.getoption('integration')")
def test_submit_pipeline(compute_pipeline_file: Path) -> None:
    resp = submit_pipeline(compute_pipeline_file)
    assert (resp.status_code == 201)