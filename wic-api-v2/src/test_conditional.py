import yaml
from pathlib import Path
import cwl_utils.parser as cwl_parser
from model import (
    CommandLineTool, Workflow,
    StepBuilder, WorkflowBuilder
)
import logging
from rich import print
import filecmp
import tempfile
import shutil

scatter_workflow_file= Path("tests/conditional-workflow.cwl")
scatter_wf = Workflow.load(scatter_workflow_file)
scatter_wf.save()
print(scatter_wf)
scatter_wf.save()
