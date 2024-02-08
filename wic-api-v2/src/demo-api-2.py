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

workflow_file= Path("/Users/antoinegerardin/Documents/projects/polus-pipelines/wic-api-v2/tests/test-data/cwl/workflow5.cwl")
wf1 = Workflow(workflow_file=workflow_file)

print(wf1)

subworkflow_file = Path("/Users/antoinegerardin/Documents/projects/polus-pipelines/wic-api-v2/tests/test-data/cwl/subworkflow1.cwl")
subworkflow = Workflow(workflow_file=subworkflow_file)


# workflow = Workflow(steps= [step1])
print(wf1)