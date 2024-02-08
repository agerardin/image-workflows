from pathlib import Path

from api import (
    Step,
    StepIO,
    IO,
    CLT,
    Workflow
)

clt_file = Path("/Users/antoinegerardin/Documents/projects/polus-pipelines/wic-api-v2/tests/test-data/cwl/echo_string.cwl")
clt = CLT(clt_file=clt_file)
print(clt)