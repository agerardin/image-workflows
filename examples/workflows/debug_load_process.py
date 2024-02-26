from pathlib import Path
from polus.pipelines.workflows import Process




def test_load_process(test_data_dir: Path, filename: str):
    cwl_file = test_data_dir / filename
    wf1 = Process.load(cwl_file)
    print(wf1)


test_data_dir = Path() / "tests" / "workflows" / "test_data"
filename = "workflow5.cwl"
test_load_process(test_data_dir, filename)


filename = "scatter-workflow1.cwl"
test_load_process(test_data_dir, filename)


filename = "nested_types3.cwl"
test_load_process(test_data_dir, filename)

filename = "echo_string_v10.cwl"
test_load_process(test_data_dir, filename)