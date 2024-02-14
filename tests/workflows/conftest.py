import pytest
from pathlib import Path
import tempfile

@pytest.fixture
def test_data_dir() -> Path:
    return Path(__file__).parent.resolve() / "test_data"

@pytest.fixture
def tmp_dir() -> Path:
    return Path(tempfile.mkdtemp(suffix="test_data"))