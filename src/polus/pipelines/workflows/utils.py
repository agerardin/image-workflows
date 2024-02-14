import subprocess
from pathlib import Path

# TODO maybe add default keywords and ability to customize
def run_cwl(process_file: Path, config_file: Path):
    cmd = ["cwltool", process_file.as_posix(), config_file.as_posix()]
    proc = subprocess.run(
        args=cmd,
        capture_output=False,
        check=True,
        text=True,
        universal_newlines=True,
    )