import pytest
from pathlib import Path
import tempfile
import shutil
from typing import Iterator

@pytest.fixture
def test_data_dir() -> Path:
    return Path(__file__).parent.resolve() / "test_data"


@pytest.fixture
def tmp_dir() -> Iterator[Path]:
    tmp_dir = Path(tempfile.mkdtemp(suffix="tmp"))
    yield tmp_dir
    print(f"test folder: {tmp_dir}")
    shutil.rmtree(tmp_dir)