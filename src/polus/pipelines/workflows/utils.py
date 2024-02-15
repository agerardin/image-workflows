import subprocess
from pathlib import Path

# TODO maybe add default keywords and ability to customize
def run_cwl(process_file: Path, config_file: Path = None, extra_args : list[str] = None):
    """Run cwltool with a config file or provided parameters."""

    cmd = ["cwltool", process_file.as_posix()]
    if config_file:
        cmd.append(config_file.as_posix())
    if extra_args:
        cmd = cmd + extra_args

    subprocess.run(
        args=cmd,
        capture_output=False,
        check=True,
        text=True,
        universal_newlines=True,
    )