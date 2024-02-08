from pathlib import Path

from api import (
    Step,
    StepIO,
    IO,
    CLT,
    Workflow
)

echo_clt_file = Path("/Users/antoinegerardin/Documents/projects/polus-pipelines/wic-api-v2/tests/test-data/cwl/echo_string.cwl")
echo_clt = CLT(clt_file=echo_clt_file)
print(echo_clt)

step1 = Step(echo_clt)

# workflow = Workflow(steps= [step1])