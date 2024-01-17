"""Test fixtures.

Customize pytest cli.
Set up all data used in tests.
"""
import pytest
from pathlib import Path
from dotenv import (find_dotenv, load_dotenv)

def pytest_addoption(parser: pytest.Parser) -> None:
    """Add options to pytest."""
    parser.addoption(
        "--integration",
        action="store_true",
        dest="integration",
        default=False,
        help="run integration tests (requires access to a compute instance)",
    )


@pytest.fixture()
def spec_path() -> Path:
    """Path fixture."""
    return (Path(__file__) / ".." / "testdata/BBBC001_process.yaml").resolve(strict=True)


@pytest.fixture()
def compute_pipeline_file() -> Path:
    """Compute pipeline file fixture."""
    return (Path(__file__) / ".." / "testdata/viz_workflow_BBBC001.json").resolve(strict=True)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_setup(item): #noqa
    # make we override any existing env variables
    load_dotenv(find_dotenv(), override=True)
    yield