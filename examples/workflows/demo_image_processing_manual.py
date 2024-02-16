from pathlib import Path
from polus.pipelines.workflows import (
    CommandLineTool, Workflow,
    StepBuilder, WorkflowBuilder,
    run_cwl
)
from pprint import pprint

if __name__ == "__main__":

    config = Path("") / "step_wf_image_processing.yaml"
    run_cwl(Path(f"wf_image_processing.cwl"), config_file=config)