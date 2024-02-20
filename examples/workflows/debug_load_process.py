from pathlib import Path
from polus.pipelines.workflows import Workflow


def test_load_workflow(test_data_dir: Path, filename: str):
    cwl_file = test_data_dir / filename
    wf1 = Workflow.load(cwl_file)
    print(wf1)


test_data_dir = Path() / "tests" / "workflows" / "test_data"
filename = "workflow5.cwl"
test_load_workflow(test_data_dir, filename)


filename = "scatter-workflow1.cwl"
test_load_workflow(test_data_dir, filename)


filename = "nested_types3.cwl"
test_load_workflow(test_data_dir, filename)